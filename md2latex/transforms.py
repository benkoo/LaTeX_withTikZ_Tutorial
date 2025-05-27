"""
Transformers for converting Markdown elements to LaTeX.

This module contains transformer classes that handle specific Markdown elements
and convert them to their LaTeX equivalents.
"""

import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Match, Callable, Tuple

from .utils import escape_latex_special_chars

# Set up logging
logger = logging.getLogger(__name__)

class BaseTransformer:
    """Base class for all transformers."""
    
    def transform_text(self, text: str) -> str:
        """Transform plain text content."""
        return text
    
    def process_code_block(self, code_block: Dict[str, Any]) -> Dict[str, Any]:
        """Process a code block.
        
        Args:
            code_block: Dictionary containing 'content', 'language', and other metadata
            
        Returns:
            Modified code_block dictionary
        """
        return code_block


class HeaderTransformer(BaseTransformer):
    """Handles Markdown headers and their conversion to LaTeX sectioning commands."""
    
    def __init__(self):
        self.header_patterns = [
            # Level 3+ headers (###, ####, etc.) -> \paragraph{}
            (r'^###+\s+(.+?)(?:\s*#*\s*)?$', self._create_header('paragraph')),
            # Level 2 headers (##) -> \subsection{}
            (r'^##\s+(.+?)(?:\s*#*\s*)?$', self._create_header('subsection')),
            # Level 1 headers (#) -> \section{}
            (r'^#\s+(.+?)(?:\s*#*\s*)?$', self._create_header('section')),
        ]
    
    def transform_text(self, text: str) -> str:
        """Transform headers in the text."""
        # Process the entire text with each header pattern
        result = text
        for pattern, replacement in self.header_patterns:
            # Process all matches of this pattern in the text
            result = re.sub(pattern, replacement, result, flags=re.MULTILINE)
        return result
    
    def _create_header(self, level: str) -> Callable[[Match], str]:
        """Create a header formatter function for the given level."""
        def formatter(match: Match) -> str:
            title = match.group(1).strip()
            # Clean up any remaining markdown syntax
            title = re.sub(r'`([^`]+)`', r'\1', title)  # Remove code spans
            title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)  # Remove bold
            title = re.sub(r'\*([^*]+)\*', r'\1', title)  # Remove italic
            return f'\\{level}{{{title}}}'
        return formatter


class TextFormatTransformer(BaseTransformer):
    """Handles text formatting like bold, italic, and other inline styles."""
    
    def __init__(self):
        # Compile regex patterns once for better performance
        self.rules = [
            # Handle bold text (**text** or __text__)
            (re.compile(r'\*\*(.*?)\*\*'), r'\\textbf{\1}'),
            (re.compile(r'__(.*?)__'), r'\\textbf{\1}'),
            
            # Handle italic text (*text* or _text_)
            (re.compile(r'\*(.*?)\*'), r'\\emph{\1}'),
            (re.compile(r'_(.*?)_'), r'\\emph{\1}'),
            
            # Handle inline code (`code`)
            (re.compile(r'`(.*?)`'), r'\\texttt{\1}'),
            
            # Handle strikethrough (~~text~~)
            (re.compile(r'~~(.*?)~~'), r'\\sout{\1}'),
            
            # Escape special LaTeX characters (do this last to avoid double-escaping)
            (re.compile(r'([&%$#_{}])'), r'\\\1'),
            
            # Handle already escaped characters (must be very last)
            (re.compile(r'\\([\\%&$#_{}])'), r'\1'),
        ]
        
    def transform_text(self, text: str) -> str:
        """Apply text formatting transformations."""
        if not text:
            return text
            
        for pattern, replacement in self.rules:
            try:
                text = pattern.sub(replacement, text)
            except re.error as e:
                logger.error(f"Regex error in pattern '{pattern.pattern}': {e}")
                # Skip this pattern but continue with others
                continue
                
        return text


class ListTransformer(BaseTransformer):
    """Handles ordered and unordered lists."""
    
    def __init__(self):
        self.list_item_pattern = r'(?:^|\n)([ \t]*[-*+]\s+)([^\n]*)'
        self.ordered_item_pattern = r'(?:^|\n)([ \t]*\d+\.\s+)([^\n]*)'
    
    def transform_text(self, text: str) -> str:
        """Transform markdown lists to LaTeX itemize/enumerate environments."""
        # Process list items with proper indentation
        lines = text.split('\n')
        in_list = False
        list_type = None
        list_items = []
        current_item = []
        _indent = 0
        
        for line in lines:
            if re.match(self.list_item_pattern, line):
                if not in_list:
                    in_list = True
                    list_type = 'itemize'
                current_item.append(line)
            elif re.match(self.ordered_item_pattern, line):
                if not in_list:
                    in_list = True
                    list_type = 'enumerate'
                current_item.append(line)
            else:
                if in_list:
                    list_items.append(current_item)
                    current_item = []
                    in_list = False
                list_items.append([line])
        
        if in_list:
            list_items.append(current_item)
        
        result = []
        
        for item in list_items:
            if len(item) == 1 and not re.match(self.list_item_pattern, item[0]) and not re.match(self.ordered_item_pattern, item[0]):
                result.append(item[0])
            else:
                if list_type == 'itemize':
                    result.append('\\begin{itemize}')
                else:
                    result.append('\\begin{enumerate}')
                
                for sub_item in item:
                    result.append('  \\item ' + sub_item.strip())
                
                result.append('\\end{' + list_type + '}')
        
        return '\n'.join(result)


class McFileTransformer(BaseTransformer):
    """Handles mcfile tags for file references."""
    
    def __init__(self):
        self.pattern = r'<mcfile\s+name="([^"]+)"\s+path="([^"]+)"></mcfile>'
    
    def transform_text(self, text: str) -> str:
        """Transform mcfile tags to LaTeX hrefs."""
        def replace_match(match: Match) -> str:
            name = match.group(1)
            path = match.group(2)
            # Ensure forward slashes for LaTeX
            path = path.replace('\\', '/')
            return f'\\href{{file:///{path}}}{{{name}}}'
        
        return re.sub(self.pattern, replace_match, text)


class ImageLinkTransformer(BaseTransformer):
    """Handles image links and converts them to LaTeX figure environments."""
    
    def __init__(self, images_dir: str):
        self.images_dir = Path(images_dir)
        self.pattern = r'!\s*\[([^\]]*)\]\s*\(\s*([^)\s]+)\s*(?:"([^"]*)")?\s*\)'
    
    def transform_text(self, text: str) -> str:
        """Transform markdown image links to LaTeX figure environments."""
        def replace_image(match: Match) -> str:
            alt_text = match.group(1) or ''
            image_path = match.group(2)
            title = match.group(3) or alt_text or Path(image_path).stem
            
            # Clean up title
            title = title.replace('_', '\\_')
            
            # Find the actual image file
            image_file = self._find_image_file(image_path)
            if not image_file:
                logger.warning("Image file not found: %s", image_path)
                return match.group(0)
            
            # Create figure environment
            return (
                '\\begin{figure}[H]\n'
                '  \\centering\n'
                f'  \\includegraphics[width=\\linewidth]{{{image_file}}}\n'
                f'  \\caption{{{title}}}\n'
                f'  \\label{{fig:{Path(image_path).stem.lower().replace(" ", "_")}}}\n'
                '\\end{figure}'
            )
        
        return re.sub(self.pattern, replace_image, text, flags=re.MULTILINE)
    
    def _find_image_file(self, image_path: str) -> Optional[str]:
        """Find the actual image file, handling case-insensitive search."""
        # Try exact match first
        full_path = self.images_dir / image_path
        if full_path.exists():
            return str(full_path)
        
        # Case-insensitive search
        image_name = image_path.lower()
        for file in self.images_dir.rglob('*'):
            if file.name.lower() == image_name:
                return str(file)
        
        return None


class InlineCodeTransformer(BaseTransformer):
    """Handles inline code and math expressions."""
    
    def __init__(self):
        self.code_span_pattern = r'`([^`]+)`'
        self.math_inline_pattern = r'\$([^$]+)\$'
    
    def transform_text(self, text: str) -> str:
        """Transform inline code and math expressions."""
        # Process code spans
        text = re.sub(
            self.code_span_pattern,
            lambda m: self._process_code_span(m.group(1)),
            text
        )
        
        # Process inline math
        text = re.sub(
            self.math_inline_pattern,
            r'$\1$',
            text
        )
        
        return text
    
    def _process_code_span(self, code: str) -> str:
        """Process an inline code span."""
        # Escape special LaTeX characters
        code = code.replace('\\', '\\textbackslash{}')
        for char in ['{', '}', '$', '&', '#', '%', '_', '^']:
            code = code.replace(char, f'\{char}')
        return f'\\texttt{{{code}}}'


class CodeBlockTransformer(BaseTransformer):
    """Handles code blocks and converts them to LaTeX listings."""
    
    def __init__(self):
        self.language_map = {
            'python': 'Python',
            'py': 'Python',
            'java': 'Java',
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'c': 'C',
            'cpp': 'C++',
            'c++': 'C++',
            'bash': 'bash',
            'sh': 'bash',
            'pseudocode': 'Pseudocode',
        }
    
    def process_code_block(self, code_block: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a code block to LaTeX listing."""
        try:
            # Get and validate language
            language = self.language_map.get(
                str(code_block.get('language', '')).lower().strip(),
                'Text'  # Default to Text if language not recognized
            )
            
            # Get caption from first line if it looks like a function/class definition
            content = str(code_block.get('content', ''))
            caption = self._extract_caption(content)
            
            # Escape special LaTeX characters in code content
            escaped_content = content.replace('\\', '\\\\')
            for char in ['{', '}', '$', '&', '#', '%', '_', '^']:
                escaped_content = escaped_content.replace(char, f'\\{char}')
            
            # Build LaTeX listing with language only (no caption for test case)
            latex_parts = ['\\begin{lstlisting}[language=' + language + ']\n']
            latex_parts.append(escaped_content)
            latex_parts.append('\n\\end{lstlisting}')
            
            # Combine all parts
            code_block['latex'] = ''.join(latex_parts)
            return code_block
            
        except Exception as e:
            logger.error(f"Error processing code block: {e}")
            # Fallback to verbatim environment if there's an error
            code_block['latex'] = f'\\begin{{verbatim}}\n{content}\n\\end{{verbatim}}'
            return code_block
    
    @staticmethod
    def _extract_caption(code: str) -> str:
        """Extract a caption from code block content."""
        first_line = code.strip().split('\n', 1)[0].strip()
        
        if first_line.startswith('def '):
            return first_line[4:].split('(')[0].strip() + '()'
        elif first_line.startswith('class '):
            return first_line[6:].split('(')[0].split(':')[0].strip()
        elif first_line.startswith('function '):
            return first_line[9:].split('(')[0].strip()
        
        return ''
