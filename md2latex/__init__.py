"""
Markdown to LaTeX converter package.

This package provides tools to convert Markdown documents to LaTeX format,
handling various elements like headers, code blocks, images, and custom syntax.
"""

from .converter import MarkdownToLatexConverter
from .transforms import (
    BaseTransformer,
    HeaderTransformer,
    TextFormatTransformer,
    ListTransformer,
    CodeBlockTransformer,
    ImageLinkTransformer,
    McFileTransformer,
    InlineCodeTransformer
)
from .utils import (
    escape_latex_special_chars,
    clean_header_lines,
    section_title_to_filename,
    strip_section_numbering,
    find_image_file,
    ensure_directory_exists,
    get_relative_path
)

__all__ = [
    # Main converter class
    'MarkdownToLatexConverter',
    
    # Transformers
    'BaseTransformer',
    'HeaderTransformer',
    'TextFormatTransformer',
    'ListTransformer',
    'CodeBlockTransformer',
    'ImageLinkTransformer',
    'McFileTransformer',
    'InlineCodeTransformer',
    
    # Utility functions
    'escape_latex_special_chars',
    'clean_header_lines',
    'section_title_to_filename',
    'strip_section_numbering',
    'find_image_file',
    'ensure_directory_exists',
    'get_relative_path'
]
