#!/usr/bin/env python3
"""
Test script for the Markdown to LaTeX converter.

This script tests the conversion of a Markdown file to LaTeX using the
md2latex package with simple test cases.
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add the current directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent))

from md2latex import MarkdownToLatexConverter

class TestMarkdownToLatexConverter(unittest.TestCase):
    """Test cases for the MarkdownToLatexConverter class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test output
        self.test_dir = Path(tempfile.mkdtemp(prefix="md2tex_test_"))
        self.sections_dir = self.test_dir / "sections"
        self.images_dir = self.test_dir / "images"
        
        # Create the sections directory
        self.sections_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_simple_conversion(self):
        """Test simple Markdown to LaTeX conversion."""
        # Create a simple test Markdown file
        test_md = self.test_dir / "test_simple.md"
        with open(test_md, 'w', encoding='utf-8') as f:
            f.write("""# Test Section

This is a simple test document.

## Subsection

With some **bold** and *italic* text.
""")
        
        # Initialize the converter
        converter = MarkdownToLatexConverter(
            md_file_path=str(test_md),
            sections_dir=str(self.sections_dir),
            images_dir=str(self.images_dir)
        )
        
        # Run the conversion
        success = converter.process_and_write_sections()
        self.assertTrue(success, "Simple conversion failed")
        
        # Check if the output file was created
        output_file = self.sections_dir / "test_section.tex"
        self.assertTrue(output_file.exists(), "Output file not created")
        
        # Check the content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(r"\section{Test Section}", content)
            self.assertIn(r"\subsection{Subsection}", content)
            self.assertIn("This is a simple test document.", content)
            self.assertIn(r"\textbf{bold}", content)
            self.assertIn(r"\emph{italic}", content)

    def test_code_block_conversion(self):
        """Test that code blocks are properly converted."""
        # Create a test Markdown file with a code block
        test_md = self.test_dir / "test_code.md"
        with open(test_md, 'w', encoding='utf-8') as f:
            f.write("""# Test Code Section

```python
def hello():
    print("Hello, World!")
```
""")
        
        # Initialize the converter
        converter = MarkdownToLatexConverter(
            md_file_path=str(test_md),
            sections_dir=str(self.sections_dir),
            images_dir=str(self.images_dir)
        )
        
        # Run the conversion
        success = converter.process_and_write_sections()
        self.assertTrue(success, "Code block conversion failed")
        
        # Check if the output file was created
        output_file = self.sections_dir / "test_code_section.tex"
        self.assertTrue(output_file.exists(), "Output file not created")
        
        # Check the content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(r"\section{Test Code Section}", content)
            self.assertIn(r"\begin{lstlisting}[language=Python]", content)
            self.assertIn("def hello():", content)
            self.assertIn("print(\"Hello, World!\")", content)
            self.assertNotIn("```", content, "Code block markers found in output")
    
    def test_image_handling(self):
        """Test that image references are handled correctly."""
        # Create a test Markdown file with an image
        test_md = self.test_dir / "test_image.md"
        with open(test_md, 'w', encoding='utf-8') as f:
            f.write("""# Test Image Section

![Example Image](example.png)
""")
        
        # Create a dummy image file
        (self.images_dir / "example.png").touch()
        
        # Initialize the converter
        converter = MarkdownToLatexConverter(
            md_file_path=str(test_md),
            sections_dir=str(self.sections_dir),
            images_dir=str(self.images_dir)
        )
        
        # Run the conversion
        success = converter.process_and_write_sections()
        self.assertTrue(success, "Image handling conversion failed")
        
        # Check if the output file was created
        output_file = self.sections_dir / "test_image_section.tex"
        self.assertTrue(output_file.exists(), "Output file not created")
        
        # Check the content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(r"\section{Test Image Section}", content)
            self.assertIn(r"\includegraphics", content)
            self.assertIn("example.png", content)


if __name__ == "__main__":
    unittest.main()