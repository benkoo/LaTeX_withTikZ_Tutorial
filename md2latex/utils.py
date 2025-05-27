"""
Utility functions for the Markdown to LaTeX converter.

This module provides helper functions used throughout the conversion process.
"""

import re
import os
import logging
from pathlib import Path
from typing import Optional, Match, List, Dict, Any, Callable, Tuple

# Configure logging
logger = logging.getLogger(__name__)

def escape_latex_special_chars(text: str) -> str:
    """
    Escape special LaTeX characters in the given text.
    
    Args:
        text: The text to escape
        
    Returns:
        Text with LaTeX special characters properly escaped
    """
    if not text:
        return text
    
    # First, handle backslashes
    text = text.replace('\\', '\\textbackslash{}')
    
    # Then handle other special characters
    special_chars = {
        '{': '\\{',
        '}': '\\}',
        '$': '\\$',
        '&': '\\&',
        '#': '\\#',
        '%': '\\%',
        '_': '\\_',
        '^': '\\^{}',
        '~': '\\~{}',
        '\\': '\\textbackslash{}',
    }
    
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)
    
    return text

def clean_header_lines(text: str) -> str:
    """
    Clean and normalize markdown header lines.
    
    Args:
        text: The text containing markdown headers
        
    Returns:
        Text with cleaned headers
    """
    if not text:
        return text
    
    def clean_line(line: str) -> str:
        # Remove backslashes before headers
        line = re.sub(r'^\\+(#+\s+.+)$', r'\1', line)
        
        # Normalize header syntax
        line = re.sub(r'^(#+)\s+(.+?)(?:\s*#*\s*)?$', 
                     lambda m: f"{m.group(1)} {m.group(2).strip()}", 
                     line)
        
        # Ensure proper closing of section commands
        for cmd in ['section', 'subsection', 'subsubsection', 'paragraph']:
            # Match section commands that might be missing a closing brace
            pattern1 = fr'^\\{cmd}\{{[^}}]*?$'
            pattern2 = fr'^\\{cmd}\{{[^}}]*[^}}\n]$'
            line = re.sub(pattern1, lambda m: m.group(0) + '}', line)
            line = re.sub(pattern2, lambda m: m.group(0) + '}', line)
        
        return line
    
    return '\n'.join(clean_line(line) for line in text.split('\n'))

def section_title_to_filename(title: str) -> str:
    """
    Convert a section title to a valid filename.
    
    Args:
        title: The section title
        
    Returns:
        A valid filename (without extension)
    """
    if not title:
        return "untitled"
    
    # Remove numbering (e.g., "1. Introduction" -> "Introduction")
    title = re.sub(r'^\d+[. ]*', '', title.strip())
    
    # Convert to lowercase and replace non-alphanumeric with underscores
    filename = re.sub(r'[^a-z0-9]+', '_', title.lower())
    
    # Remove leading/trailing underscores and collapse multiple underscores
    filename = re.sub(r'_+', '_', filename).strip('_')
    
    return filename if filename else "untitled"

def strip_section_numbering(header_text: str) -> str:
    """
    Strip numbering from section headers.
    
    Args:
        header_text: The header text (e.g., "1.2 Section Title")
        
    Returns:
        The header text without numbering (e.g., "Section Title")
    """
    if not header_text:
        return ""
    
    # Match patterns like "1. Text" or "1.2.3 Text"
    match = re.match(r'^(\d+(?:\.\d+)*\s*)?(.+)$', header_text.strip())
    if match and match.group(2):
        return match.group(2).strip()
    return header_text.strip()

def find_image_file(image_name: str, search_dirs: List[str]) -> Optional[str]:
    """
    Find an image file in the specified directories.
    
    Args:
        image_name: The name of the image file to find
        search_dirs: List of directories to search in
        
    Returns:
        The full path to the image if found, None otherwise
    """
    if not image_name:
        return None
    
    # Try exact match first
    for dir_path in search_dirs:
        path = Path(dir_path) / image_name
        if path.exists():
            return str(path.resolve())
    
    # Case-insensitive search
    image_name_lower = image_name.lower()
    for dir_path in search_dirs:
        try:
            for file in Path(dir_path).rglob('*'):
                if file.name.lower() == image_name_lower:
                    return str(file.resolve())
        except (OSError, PermissionError):
            continue
    
    return None

def ensure_directory_exists(path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def get_relative_path(from_path: str, to_path: str) -> str:
    """
    Get a relative path from one path to another.
    
    Args:
        from_path: The source path
        to_path: The target path
        
    Returns:
        A relative path from from_path to to_path
    """
    try:
        from_path = Path(from_path).resolve()
        to_path = Path(to_path).resolve()
        
        # If on different drives on Windows, return the absolute path
        if os.name == 'nt' and from_path.drive != to_path.drive:
            return str(to_path)
            
        return str(to_path.relative_to(from_path))
    except ValueError:
        # If we can't get a relative path, return the absolute path
        return str(to_path)
