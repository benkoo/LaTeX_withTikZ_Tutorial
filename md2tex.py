#!/usr/bin/env python3
"""
Command-line interface for the Markdown to LaTeX converter.

This script provides a simple way to convert Markdown files to LaTeX
using the md2latex package.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the current directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent))

from md2latex import MarkdownToLatexConverter


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level.
    
    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('md2tex.log')
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to LaTeX sections.'
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Path to the input Markdown file',
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='sections',
        help='Directory to store generated LaTeX sections (default: sections/)',
    )
    
    parser.add_argument(
        '-i', '--images-dir',
        type=str,
        default='images',
        help='Directory containing images (default: images/)',
    )
    
    parser.add_argument(
        '-b', '--base-dir',
        type=str,
        default=None,
        help='Base directory for output (default: directory of input file)',
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output',
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for the command-line interface.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    args = parse_arguments()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Resolve paths
        input_file = Path(args.input_file).resolve()
        
        # Set base directory
        if args.base_dir:
            base_dir = Path(args.base_dir).resolve()
        else:
            base_dir = input_file.parent
        
        # Create output directories relative to base directory
        sections_dir = base_dir / args.output_dir
        images_dir = base_dir / args.images_dir
        
        logger.info(f"Input file: {input_file}")
        logger.info(f"Sections directory: {sections_dir}")
        logger.info(f"Images directory: {images_dir}")
        
        # Ensure output directories exist
        sections_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize and run the converter
        converter = MarkdownToLatexConverter(
            md_file_path=str(input_file),
            sections_dir=str(sections_dir),
            images_dir=str(images_dir),
            base_output_dir=str(base_dir)
        )
        
        success = converter.process_and_write_sections()
        
        if success:
            logger.info("Conversion completed successfully!")
            return 0
        else:
            logger.error("Conversion failed.")
            return 1
            
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
