#!/usr/bin/env python3
"""
Convert GASing_Arithmetic.md to LaTeX and generate a PDF using the main.tex template.
"""
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union
from md2latex.converter import MarkdownToLatexConverter

# Add the current directory to the path so we can import our package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('conversion.log')
    ]
)
logger = logging.getLogger('md2latex')

def setup_output_directories(base_dir: Path) -> Tuple[Path, Path, Path]:
    """
    Set up the output directory structure.
    
    Args:
        base_dir: Base directory for outputs
        
    Returns:
        Tuple of (output_dir, tex_dir, pdf_dir) paths
    """
    try:
        # Create main output directory
        base_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created base directory: {base_dir}")
        
        # Create document directory (instead of sections)
        document_dir = base_dir / "document"
        document_dir.mkdir(exist_ok=True)
        logger.debug(f"Created document directory: {document_dir}")
        
        # Create images directory inside the document directory
        images_dir = document_dir / "images"
        images_dir.mkdir(exist_ok=True)
        logger.debug(f"Created images directory: {images_dir}")
        
        return document_dir, document_dir, document_dir
        
    except OSError as e:
        logger.error(f"Failed to create output directories: {e}")
        raise

def run_command(cmd: Union[List[str], str], cwd: Optional[Path] = None) -> bool:
    """
    Run a shell command and return True if successful.
    
    Args:
        cmd: Command to run (as string or list of args)
        cwd: Working directory for the command
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    try:
        logger.debug(f"Running command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            shell=isinstance(cmd, str),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            errors='replace'
        )
        logger.debug(f"Command output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {e.cmd}")
        logger.error(f"Output: {e.output}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        return False

def generate_pdf(tex_file: Path, output_dir: Path) -> bool:
    """
    Generate a PDF from a LaTeX file.
    
    Args:
        tex_file: Path to the .tex file
        output_dir: Directory to save the PDF
        
    Returns:
        bool: True if PDF generation was successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the directory containing the tex file
        tex_dir = tex_file.parent
        tex_filename = tex_file.name
        
        # Run pdflatex
        cmd = [
            'pdflatex',
            '-interaction=nonstopmode',
            f'-output-directory={output_dir}',
            tex_filename
        ]
        
        logger.info(f"Running LaTeX command: {' '.join(cmd)} in {tex_dir}")
        
        # Run multiple times to resolve references
        for _ in range(3):
            result = subprocess.run(
                cmd,
                cwd=str(tex_dir),
                capture_output=True,
                text=True
            )
            
            # Check for errors
            if result.returncode != 0:
                error_msg = f"LaTeX compilation failed with return code {result.returncode}"
                logger.error(error_msg)
                
                # Write error log
                error_log = output_dir / 'latex_compile_error.log'
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(f"{error_msg}\n")
                    f.write("\n=== STDOUT ===\n")
                    f.write(result.stdout)
                    f.write("\n\n=== STDERR ===\n")
                    f.write(result.stderr)
                
                logger.error(f"See error log for details: {error_log}")
                return False
        
        # Check if PDF was created
        pdf_file = output_dir / f"{tex_file.stem}.pdf"
        if not pdf_file.exists():
            error_msg = "PDF file was not created during compilation"
            logger.error(error_msg)
            return False
            
        logger.info(f"Successfully generated PDF: {pdf_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return False

def create_main_tex(output_dir: Path, content: str, template_path: Optional[Path] = None) -> Path:
    """
    Create a main.tex file that includes the generated LaTeX content.
    
    Args:
        output_dir: Directory where the main.tex file will be created
        content: The LaTeX content to include
        template_path: Optional path to a custom template file
        
    Returns:
        Path to the created main.tex file
    """
    try:
        # Create figures directory if it doesn't exist
        figures_dir = output_dir / 'figures'
        figures_dir.mkdir(exist_ok=True)
        
        # Copy the macro file if it exists in the template directory
        macro_file = Path(__file__).parent / 'figures' / 'spivak_fong_wd_macros.tex'
        if macro_file.exists():
            import shutil
            shutil.copy(macro_file, figures_dir / 'spivak_fong_wd_macros.tex')
            logger.info(f"Copied macro file to {figures_dir}")
            
        # Copy arxiv.sty if it exists
        arxiv_style = Path(__file__).parent / 'arxiv.sty'
        if arxiv_style.exists():
            shutil.copy(arxiv_style, output_dir / 'arxiv.sty')
            logger.info(f"Copied arxiv.sty to {output_dir}")
        
        # Use default template if none provided
        if template_path is None:
            template_path = Path(__file__).parent / 'main.tex'
            
        # Read the template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # Fix the macro file path in the template
        template = template.replace(
            '\input{figures/spivak_fong_wd_macros.tex}',
            '\input{./figures/spivak_fong_wd_macros.tex}'
        )
            
        # Remove any duplicate geometry package usages
        import re
        template = re.sub(r'\\usepackage\[.*?\]{geometry}', '', template)
        
        # Remove any section includes that might cause issues
        template = re.sub(r'\\input\{sections/.*?\}', '', template)
        
        # Insert the content before the document end
        if '\end{document}' in template:
            # Insert our content before the end of document
            template = template.replace('\end{document}', 
                                     f"\\begin{{document}}\n                                     {content}\n"
                                     "\end{document}")
        
        # Write the main.tex file
        output_file = output_dir / 'main.tex'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template)
            
        logger.info(f"Created main.tex file at {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating main.tex file: {e}", exc_info=True)
        raise
        new_content = (
            template[:doc_start] + 
            '\n% Generated content starts here\n' +
            content.strip() + 
            '\n% Generated content ends here\n\n' +
            template[doc_end:]
        )
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the main.tex file
        main_tex = output_dir / 'main.tex'
        try:
            main_tex.write_text(new_content, encoding='utf-8')
            logger.info(f"Successfully created {main_tex}")
            return main_tex
        except IOError as e:
            error_msg = f"Failed to write {main_tex}: {e}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
            
    except Exception as e:
        logger.exception("Unexpected error in create_main_tex")
        raise

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert GASing Arithmetic Markdown to LaTeX and generate PDF.'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        default=None,
        help='Path to input Markdown file (default: wip/experiments/GASing_Arithmetic.md)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output directory (default: gasing_arithmetic_output)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()

def main() -> int:
    """
    Main function to convert Markdown to LaTeX and generate PDF.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Configure logging level
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")
        
        # Set up paths
        project_root = Path(__file__).parent
        output_base = project_root / (args.output or "gasing_arithmetic_output")
        
        # Set up output directories
        logger.info(f"Setting up output directory: {output_base}")
        try:
            output_dir, tex_dir, pdf_dir = setup_output_directories(output_base)
        except OSError as e:
            logger.error(f"Failed to create output directories: {e}")
            return 1
        
        # Locate the input Markdown file
        md_file = (
            Path(args.input) if args.input
            else project_root.parent / "wip" / "experiments" / "GASing_Arithmetic.md"
        )
        
        if not md_file.exists():
            logger.error(f"Markdown file not found: {md_file}")
            return 1
        
        logger.info(f"Converting {md_file} to LaTeX...")
        
        try:
            # Initialize the converter with the correct paths
            converter = MarkdownToLatexConverter(
                str(md_file),
                sections_dir=str(tex_dir / 'sections'),  # Store sections in a subdirectory
                images_dir=str(tex_dir / 'images')
            )
            
            # Convert markdown to LaTeX content
            logger.debug("Converting Markdown to LaTeX...")
            
            # First, read the markdown content
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
            except Exception as e:
                logger.error(f"Failed to read markdown file: {e}")
                return 1
            
            # Process the markdown content through the converter
            try:
                # Convert markdown to LaTeX and write sections
                success = converter.process_and_write_sections()
                if not success:
                    logger.error("Failed to convert markdown to LaTeX")
                    return 1
                
                # Get the generated LaTeX content
                latex_content = converter.get_latex_content()
                if not latex_content:
                    logger.error("No LaTeX content was generated")
                    return 1
                
                # Create the main.tex file with the LaTeX content
                main_tex = create_main_tex(output_dir, latex_content)
                if not main_tex or not main_tex.exists():
                    logger.error(f"Failed to create main LaTeX file: {main_tex}")
                    return 1
                
                logger.info(f"Successfully generated LaTeX document: {main_tex}")
                
                # Generate PDF
                logger.info("Generating PDF...")
                if generate_pdf(main_tex, output_dir):
                    pdf_file = output_dir / main_tex.with_suffix('.pdf').name
                    logger.info(f"Successfully generated PDF: {pdf_file}")
                    return 0
                else:
                    logger.error("Failed to generate PDF - check the log file for details")
                    return 1
                    
            except Exception as e:
                logger.exception(f"Error during markdown conversion: {e}")
                return 1
                
        except Exception as e:
            logger.exception("An error occurred during conversion:")
            return 1
            
    except Exception as e:
        logger.exception("Unexpected error in main:")
        return 1
    finally:
        # Ensure all handlers are flushed
        for handler in logger.handlers:
            handler.flush()

if __name__ == "__main__":
    sys.exit(main())
