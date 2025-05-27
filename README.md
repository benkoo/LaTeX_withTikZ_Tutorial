# LaTeX with TikZ Paper Compilation Project

This repository helps you compile and produce academic papers in LaTeX, with a focus on TikZ for high-quality diagrams and illustrations.

## Features

- **Modular Structure:** Organized into sections for easy editing and collaboration
- **TikZ Integration:** Example figures and diagrams for various concepts
- **Automated Build:** `Makefile` automates the compilation process
- **Markdown Support:** Convert Markdown content to LaTeX
- **Version Control Friendly:** `.gitignore` excludes build artifacts

## Prerequisites

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Python 3.6+ (for conversion scripts)
- Required Python packages: `pypandoc`, `python-dotenv`

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LaTeX_withTikZ_Tutorial
   ```

2. **Setup environment**
   - Copy `.env.example` to `.env`
   - Update the `MC_SOURCE` variable in `.env` to point to your Markdown file
   - Copy `author_info.example.tex` to `.author_info.tex` and edit with your details

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt  # If requirements.txt exists
   pip install pypandoc python-dotenv
   ```

## Building the PDF

1. **Prepare your content**
   - Place your Markdown files in the project root or `md/` directory
   - Add TikZ figures in the `figures/` directory
   - Update `main.tex` to include any new sections

2. **Build the document**
   ```bash
   make clean    # Optional: Clean previous builds
   make          # Build the PDF
   ```
   The output will be `main.pdf`

3. **Clean up**
   ```bash
   make clean    # Remove build artifacts
   ```

## Project Structure

- `main.tex` - Main LaTeX document
- `sections/` - Individual sections (included in main.tex)
- `figures/` - TikZ source files for diagrams
- `md/` - Source Markdown files
- `.author_info.tex` - Author information (not version controlled)
- `Makefile` - Build automation
- `auto_transcribe_md_to_tex.py` - Converts Markdown to LaTeX
- `validate_markdown_structure.py` - Validates Markdown structure

## Customization

1. **Adding Content**
   - Add new Markdown files in the `md/` directory
   - Reference them in your `.env` file
   - The build process will automatically convert them to LaTeX

2. **Adding TikZ Figures**
   - Create new `.tex` files in the `figures/` directory
   - Reference them in your Markdown using `\input{figures/filename.tex}`

3. **Modifying Styles**
   - Edit `main.tex` for document-wide changes
   - Add custom LaTeX packages as needed

## Troubleshooting

- **Missing packages**: Install missing LaTeX packages using your distribution's package manager
- **Build errors**: Check `main.log` for detailed error messages
- **Markdown conversion issues**: Run the conversion script manually for debugging:
  ```bash
  python3 auto_transcribe_md_to_tex.py your_file.md
  ```

## License

This project is intended for academic and educational use. Please adapt and extend it for your own research papers and reports.

## License

This project is intended for academic and educational use. Please adapt and extend it for your own research papers and reports.

---

## Acknowledgments

This paper and repository explicitly use information, examples, and diagram code from the [TikZ.dev](https://tikz.dev) website. We thank the TikZ.dev authors and community for providing high-quality documentation and inspiration for TikZ graphics.

For questions or contributions, please open an issue or submit a pull request.
```
