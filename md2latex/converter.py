"""
Main converter module for Markdown to LaTeX conversion.

This module provides the MarkdownToLatexConverter class which handles the overall
conversion process from Markdown to LaTeX format.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Pattern, Match, Callable, Any, Union, Tuple

from . import transforms
from .utils import (
    escape_latex_special_chars,
    clean_header_lines,
    section_title_to_filename,
    strip_section_numbering
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class MarkdownToLatexConverter:
    """
    Converts Markdown files to LaTeX format.
    
    This class handles the overall conversion process, including file I/O,
    section extraction, and applying various transformations to convert
    Markdown syntax to LaTeX.
    """
    
    def __init__(self, md_file_path: str, sections_dir: str = "sections", 
                 images_dir: str = "images", base_output_dir: Optional[str] = None):
        """
        Initialize the converter with file paths and directories.
        
        Args:
            md_file_path: Path to the input Markdown file
            sections_dir: Directory to store generated LaTeX sections
            images_dir: Directory containing images referenced in the Markdown
            base_output_dir: Base directory for output (defaults to current directory)
        """
        self.md_file_path = Path(md_file_path).resolve()
        self.base_output_dir = Path(base_output_dir) if base_output_dir else Path.cwd()
        
        # Resolve relative paths from the base output directory
        self.sections_dir = self.base_output_dir / sections_dir
        self.images_dir = self.base_output_dir / images_dir
        
        # Ensure output directories exist
        self.sections_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize transformers
        self.transformers = [
            transforms.HeaderTransformer(),
            transforms.TextFormatTransformer(),
            transforms.ListTransformer(),
            transforms.McFileTransformer(),
            transforms.ImageLinkTransformer(str(self.images_dir)),
            transforms.InlineCodeTransformer(),
            transforms.CodeBlockTransformer()
        ]
    
    def process_and_write_sections(self) -> bool:
        """
        Process the markdown file and write LaTeX sections to output files.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Read markdown content
            md_content = self._read_markdown_file()
            if not md_content:
                return False
            
            # Extract sections
            sections = self.extract_sections(md_content)
            if not sections:
                logger.warning("No sections found in the Markdown file.")
                return False
            
            # Process and write sections
            self._write_sections(sections)
            logger.info(f"Successfully processed {len(sections)} sections.")
            return True
            
        except Exception as e:
            logger.error(f"Error during processing: {e}", exc_info=True)
            return False
    
    def _read_markdown_file(self) -> str:
        """Read and return the content of the markdown file."""
        try:
            with open(self.md_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Markdown file not found: {self.md_file_path}")
        except Exception as e:
            logger.error(f"Error reading Markdown file {self.md_file_path}: {e}")
        return ""
    
    def extract_sections(self, md_content: str) -> List[Dict[str, str]]:
        """
        Extract sections from markdown content.
        
        Args:
            md_content: The markdown content to process
            
        Returns:
            List of section dictionaries with 'title', 'content', and 'filename' keys
        """
        sections = []
        # Split content by top-level sections (single #)
        section_pattern = r'(^#\s+(.+?))\n([\s\S]*?)(?=^#\s|\Z)'
        
        for match in re.finditer(section_pattern, md_content, flags=re.MULTILINE):
            header_line = match.group(1).strip()
            title = match.group(2).strip()
            content = (header_line + '\n' + (match.group(3) or '').strip()).strip()
            filename = section_title_to_filename(title) + '.tex'
            sections.append({
                'title': title,
                'content': content,
                'filename': filename
            })
            
        # If no sections found, treat the entire content as one section
        if not sections and md_content.strip():
            title = Path(self.md_file_path).stem.replace('_', ' ').title()
            filename = section_title_to_filename(title) + '.tex'
            sections.append({
                'title': title,
                'content': md_content.strip(),
                'filename': filename
            })
            
        return sections
    
    def _write_sections(self, sections: List[Dict[str, str]]) -> None:
        """
        Write sections to individual LaTeX files.
        
        Args:
            sections: List of section dictionaries with 'content' and 'filename' keys
        """
        for section in sections:
            out_path = self.sections_dir / section['filename']
            try:
                latex_content = self.convert_section_to_latex(section['content'])
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                logger.debug(f"Wrote {out_path} ({len(latex_content)} chars)")
            except Exception as e:
                logger.error(f"Error writing LaTeX file {out_path}: {e}")
    
    def convert_section_to_latex(self, md_content: str) -> str:
        """
        Convert a markdown section to LaTeX.
        
        Args:
            md_content: Markdown content of a single section
            
        Returns:
            LaTeX formatted string
        """
        try:
            # Split into segments (code blocks and text)
            segments = self._split_into_segments(md_content)
            
            # Process each segment
            latex_parts = []
            for segment in segments:
                try:
                    if segment['type'] == 'text':
                        # Apply text transformations
                        text = segment['content']
                        for transformer in self.transformers:
                            if hasattr(transformer, 'transform_text'):
                                try:
                                    text = transformer.transform_text(text)
                                except re.error as e:
                                    logger.error(f"Regex error in {transformer.__class__.__name__} with text: {text[:100]}...")
                                    raise
                        latex_parts.append(text)
                        
                    elif segment['type'] == 'code':
                        # Process code blocks
                        code_block = {
                            'content': segment['content'],
                            'language': segment['language']
                        }
                        for transformer in self.transformers:
                            if hasattr(transformer, 'process_code_block'):
                                code_block = transformer.process_code_block(code_block)
                        latex_parts.append(code_block.get('latex', ''))
                except Exception as e:
                    logger.error(f"Error processing segment: {segment.get('type', 'unknown')}")
                    raise
            
            return "".join(latex_parts)
        except Exception as e:
            logger.error(f"Error in convert_section_to_latex: {str(e)}")
            logger.error(f"Content causing error: {md_content[:200]}...")
            raise
    
    @staticmethod
    def _split_into_segments(md_content: str) -> List[Dict[str, Any]]:
        """
        Split markdown content into segments (text and code blocks).
        
        Args:
            md_content: The markdown content to split
            
        Returns:
            List of segment dictionaries with 'type', 'content', and other metadata
        """
        segments = []
        last_end = 0
        
        # Find all code blocks (```lang ... ```)
        code_block_pattern = re.compile(
            r'```(\w*)\s*\n([\s\S]*?)\n```\s*$',
            re.MULTILINE
        )
        for match in code_block_pattern.finditer(md_content):
            # Add text before the code block
            if match.start() > last_end:
                segments.append({
                    'type': 'text',
                    'content': md_content[last_end:match.start()]
                })
            
            # Add the code block
            lang = match.group(1) or 'text'
            segments.append({
                'type': 'code',
                'content': match.group(2),
                'language': lang
            })
            
            last_end = match.end()
        
        # Add remaining text after the last code block
        if last_end < len(md_content):
            segments.append({
                'type': 'text',
                'content': md_content[last_end:]
            })
        
        return segments
