import os
import re
import glob
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MarkdownToLatexConverter:
    def __init__(self, md_file_path, sections_dir="sections", images_dir="images"):
        self.md_file_path = md_file_path
        self.sections_dir = sections_dir
        self.images_dir = images_dir
        self.base_output_dir = os.path.dirname(os.path.abspath('main.tex')) # Assuming main.tex is in the script's CWD for LaTeX

        os.makedirs(self.sections_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True) # Ensure images dir from original script logic

        # Define transformation rules: (pattern, replacement_or_handler, scope, order)
        # Order can be used if sequence of application is critical for some rules.
        self.transformation_rules = [
            # Text processing rules (applied to non-code segments)
            # Headers - process deeper levels first
            (r'^\s*#{3,}\s+(.+)$', lambda m: '\\paragraph{' + self._strip_section_numbering(m.group(1)) + '}', 'text', 10),
            (r'^\s*#{2}\s+(.+)$', lambda m: '\\subsection{' + self._strip_section_numbering(m.group(1)) + '}', 'text', 20),
            (r'^\s*#{1}\s+(.+)$', lambda m: '\\section{' + self._strip_section_numbering(m.group(1)) + '}', 'text', 30),
            # Defensive header catch-all (if any missed)
            (r'^\s*\\*#+\s+(.+)$', lambda m: '\\' + ('sub' * min(2, m.group(0).count('#')-1)) + 'section{' + self._strip_section_numbering(m.group(1).strip()) + '}', 'text', 40),
            (r'^(?P<pre>[^\\][^#]*?)#', lambda m: m.group('pre') + r'\\#', 'text', 50), # Escape stray # not at start of line or after command
            
            # Bold and Italics
            (r'\[\[([^\]]+)\]\]', r'\\textbf{\\textit{\1}}', 'text', 60), # [[text]] for bold italics
            (r'\*\*(.+?)\*\*', r'\\textbf{\1}', 'text', 70),
            (r'\*(.+?)\*', r'\\emph{\1}', 'text', 80),

            # Lists - Labeled dash bullets first
            (r'(^|\n)[ \t]*-[ \t]*([^\n:]+):[ \t]*(.+)', r'\1\n\\noindent\\textbf{\2:} \3\n', 'text', 90),
            # Regular dash bullets
            (r'(^|\n)[ \t]*-[ \t]*(?!\\noindent)(.+)', r'\1\n\\noindent \2\n', 'text', 100),
            
            # Star bullets - Labeled with description and optional following content
            (r'(^|\n)\s*\*\s+([^\n:]+):\s*([^\n]+)(?:\n+([^\n*][^\n]+(?:\n+(?!\s*\*\s+)[^\n]+)*))?', self._process_labeled_star_bullets, 'text', 110),
            # Regular star bullets with optional following content
            (r'(^|\n)\s*\*\s+([^\n:][^\n]*)(?:\n+([^\n*][^\n]+(?:\n+(?!\s*\*\s+)[^\n]+)*))?', self._process_regular_star_bullets, 'text', 120),
            # Simple star bullets (no extensive following content)
            (r'(^|\n)\s*\*\s+([^\n]+)(?!\n+(?!\s*\*\s+)[^\n]+)', self._process_simple_star_bullet, 'text', 130),

            # mcfile tags
            (r'<mcfile\s+name="([^"]+)"\s+path="([^"]+)"></mcfile>', 
             lambda m: f'\\textit{{\\href{{file://{{{m.group(2)}}}}}{{{m.group(1)}}}}}', 'text', 140),
            
            # Em-dash spacing (ensure space after --- if not followed by space)
            (r'---(?!\\s)', '--- ', 'text', 145),

            # Inline code (must be processed carefully after other text elements)
            (r'`([^`]+)`', self._process_inline_code_segment, 'text', 150),
            
            # General underscore escaping (late, to avoid interfering with specific syntax)
            (r'(?<!\\)_', r'\\_', 'text', 160),
        ]

    def _section_title_to_filename(self, title):
        title = re.sub(r"^\d+[. ]*", "", title.strip())
        title = title.lower()
        title = re.sub(r"[^a-z0-9]+", "_", title)
        title = re.sub(r"_+", "_", title).strip('_')
        return f"{title}.tex"

    def _strip_section_numbering(self, header_text):
        return re.sub(r'^(\d+(\.\d+)*)\s+(.+)$', r'\3', header_text)

    def _clean_header_lines(self, text):
        text = re.sub(r'^\\+(#+)\s+(.+)$', r'\1 \2', text, flags=re.MULTILINE)
        text = re.sub(r'^\\##\s+##\s+(.+)$', r'#### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^(#+)\s+(.+)$', lambda m: '#' * len(m.group(1)) + ' ' + m.group(2), text, flags=re.MULTILINE)
        text = re.sub(r'^\\(#+\s+.+)$', r'\1', text, flags=re.MULTILINE)
        # Ensure section commands have proper closing braces
        for cmd in ['section', 'subsection', 'subsubsection', 'paragraph']:
            text = re.sub(r'^(\\' + cmd + r'\{[^}]*?)$', r'\1}', text, flags=re.MULTILINE)
            text = re.sub(r'^(\\' + cmd + r'\{[^}]*[^}\n])$', r'\1}', text, flags=re.MULTILINE)
        text = re.sub(r'^}\s*$', '', text, flags=re.MULTILINE) # Remove standalone closing braces
        return text

    def _find_image_file(self, image_name):
        if not os.path.exists(self.images_dir):
            return None
        image_files = glob.glob(os.path.join(self.images_dir, '*'))
        for file_path in image_files:
            if os.path.basename(file_path) == image_name:
                return file_path
        image_name_lower = image_name.lower()
        for file_path in image_files:
            if os.path.basename(file_path).lower() == image_name_lower:
                return file_path
        return None

    def _process_image_links(self, text):
        def replace_image(match):
            full_match, label, image_name = match.group(0), match.group(1).strip(), match.group(2).strip()
            if not image_name:
                return full_match
            
            image_file = self._find_image_file(image_name)
            if not image_file:
                logging.warning(f"Image '{image_name}' not found in {self.images_dir}")
                return full_match
            
            try:
                rel_path = os.path.relpath(os.path.abspath(image_file), self.base_output_dir)
                rel_path = rel_path.replace('\\', '/').replace('//', '/')
                base_name = os.path.splitext(os.path.basename(image_name))[0]
                safe_label = re.sub(r'[^a-zA-Z0-9]', '', base_name).lower()
                caption = label if label else base_name.replace('_', ' ').title()
                
                return (
                    '\n\\begin{figure}[H]\n'
                    '  \\centering\n'
                    f'  \\includegraphics[width=\\linewidth]{{{rel_path}}}\n'
                    f'  \\caption{{{caption}}}\n'
                    f'  \\label{{fig:{safe_label}}}\n'
                    '\\end{figure}\n'
                )
            except Exception as e:
                logging.error(f"Error processing image {image_name}: {str(e)}")
                return full_match
        
        pattern = r'!\s*\[([^\]]*)\]\s*\(\s*([^)\s]+)\s*\)'
        return re.sub(pattern, replace_image, text, flags=re.MULTILINE)

    def _process_inline_code_segment(self, match):
        code_text = match.group(1)
        if code_text is None: code_text = '' # Ensure code_text is a string

        escaped_sequences = {}
        def preserve_escapes(m):
            placeholder = f"__ESCAPED_SEQ_{len(escaped_sequences)}__"
            escaped_sequences[placeholder] = m.group(0)
            return placeholder
        code_text = re.sub(r'\\([\\%&$#_{}^~])', preserve_escapes, code_text)

        math_patterns = [
            (r'\(([^\)]+?)\^([^\)]+?)\s*-\s*([^\)]+?)\)', r'$(\1^{\2} - \3)$'),
            (r'(\w+)\^(\w+)', r'$\1^{\2}$'),
            (r'(\w+)_(\w+)', r'$\1_{\2}$'),
        ]
        for pattern, replacement in math_patterns:
            code_text = re.sub(pattern, replacement, code_text)
        
        code_text = re.sub(r'\^(?![{\w])', r'\\^{}', code_text) # Caret escaping

        def escape_outside_math(text_segment):
            parts = re.split(r'(\$[^\$]*\$)', text_segment)
            result = []
            for i, part in enumerate(parts):
                if i % 2 == 1: result.append(part)
                else:
                    escaped_part = part
                    for char in ['%', '&', '#', '_', '~']:
                        escaped_part = escaped_part.replace(char, f'\\{char}')
                    result.append(escaped_part)
            return ''.join(result)
        
        code_text = escape_outside_math(code_text)

        for placeholder, original in escaped_sequences.items():
            code_text = code_text.replace(placeholder, original)
        
        return f'\\texttt{{{code_text}}}'

    # Bullet point handlers (from original script, adapted)
    def _process_labeled_star_bullets(self, match):
        prefix, label, description, following_content_raw = match.groups()
        label = label.strip()
        description = description.strip()
        following_content = ""
        if following_content_raw:
            content_lines = [line.strip() for line in following_content_raw.strip().split('\n')]
            content_text = ' '.join(content_lines)
            following_content = f"\n\n\\vspace{{0.5em}}\n\\noindent\\hspace{{2em}}{content_text}\n\\vspace{{0.5em}}\n"
        return f"{prefix or ''}\\begin{{itemize}}\n\\item \\textbf{{{label}:}} {description}{following_content}\n\\end{{itemize}}\n"

    def _process_regular_star_bullets(self, match):
        prefix, bullet_text, following_content_raw = match.groups()
        bullet_text = bullet_text.strip()
        following_content = ""
        if following_content_raw:
            content_lines = [line.strip() for line in following_content_raw.strip().split('\n')]
            content_text = ' '.join(content_lines)
            following_content = f"\n\n\\vspace{{0.5em}}\n\\noindent\\hspace{{2em}}{content_text}\n\\vspace{{0.5em}}\n"
        return f"{prefix or ''}\\begin{{itemize}}\n\\item {bullet_text}{following_content}\n\\end{{itemize}}\n"

    def _process_simple_star_bullet(self, match):
        prefix, bullet = match.groups()
        bullet = bullet.strip()
        if ':' in bullet and not bullet.startswith('\\'):
            label, desc = bullet.split(':', 1)
            return f"{prefix or ''}\\begin{{itemize}}\n\\item \\textbf{{{label.strip()}:}} {desc.strip()}\n\\end{{itemize}}\n"
        return f"{prefix or ''}\\begin{{itemize}}\n\\item {bullet}\n\\end{{itemize}}\n"

    def _convert_text_segment(self, text_segment):
        # Apply general text transformations based on rules
        # Ensure headers are cleaned first
        processed_segment = self._clean_header_lines(text_segment)
        
        # Apply ordered transformation rules
        # Sort rules by 'order' if provided, else default to 0
        sorted_rules = sorted([rule for rule in self.transformation_rules if rule[2] == 'text'], key=lambda r: r[3] if len(r) > 3 else 0)

        for pattern, replacement_or_handler, scope, *_ in sorted_rules:
            if callable(replacement_or_handler):
                processed_segment = re.sub(pattern, replacement_or_handler, processed_segment, flags=re.MULTILINE)
            else:
                processed_segment = re.sub(pattern, replacement_or_handler, processed_segment, flags=re.MULTILINE)
        return processed_segment

    def convert_section_content_to_latex(self, md_content):
        # Preprocessing: Handle image links first as they introduce block elements
        md_content = self._process_image_links(md_content)

        # Split into code blocks and text segments
        segments = []
        last_end = 0
        # Regex for code blocks ```lang\ncode``` or ```\ncode```
        for match in re.finditer(r'```(?:([a-zA-Z0-9_+-]*))?\s*\n([\s\S]*?)```', md_content):
            if match.start() > last_end:
                segments.append({'type': 'text', 'content': md_content[last_end:match.start()]})
            
            lang = match.group(1) or 'Python' # Default to Python
            code = match.group(2)
            segments.append({'type': 'code', 'content': code, 'language': lang})
            last_end = match.end()
        
        if last_end < len(md_content):
            segments.append({'type': 'text', 'content': md_content[last_end:]})

        latex_parts = []
        for segment in segments:
            if segment['type'] == 'text':
                latex_parts.append(self._convert_text_segment(segment['content']))
            elif segment['type'] == 'code':
                code_content = segment['content']
                lang = segment['language']
                listings_lang_map = {
                    'python': 'Python', 'py': 'Python', 'java': 'Java', 
                    'javascript': 'JavaScript', 'js': 'JavaScript', 'c': 'C', 
                    'cpp': 'C++', 'c++': 'C++', 'bash': 'bash', 'sh': 'bash',
                    'pseudocode': 'Pseudocode', # Added from original
                }
                listings_lang = listings_lang_map.get(lang.lower(), 'Python')
                
                caption = ''
                # Simplified caption extraction from original script
                if code_content.strip().startswith(('def ', 'function ', 'class ', '# ')):
                    first_line = code_content.strip().split('\n')[0].strip()
                    for prefix in ['def ', 'function ', 'class ', '# ']:
                        if first_line.startswith(prefix):
                            caption = first_line[len(prefix):].split('(')[0].strip() + ' Algorithm'
                            break
                escaped_caption = caption.replace('_', r'\_') if caption else ""
                caption_text = f",caption={{{escaped_caption}}}" if caption else ""
                
                tex_code = f"\\begin{{lstlisting}}[language={listings_lang}{caption_text}]\n{code_content.rstrip()}\n\\end{{lstlisting}}"
                latex_parts.append(tex_code)
        
        return "".join(latex_parts)

    def extract_sections_from_md(self, md_text):
        # Original logic: find top-level sections (##) and their content
        section_pattern = r'^##\s+(.+?)\n([\s\S]*?)(?=^##\s+|\Z)'
        matches = re.finditer(section_pattern, md_text, flags=re.MULTILINE)
        sections_data = []
        for match in matches:
            title = match.group(1).strip()
            content = match.group(2).strip()
            filename = self._section_title_to_filename(title)
            sections_data.append({'filename': filename, 'title': title, 'content': content})
        return sections_data

    def process_and_write_sections(self):
        try:
            with open(self.md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
        except FileNotFoundError:
            logging.error(f"Markdown file not found: {self.md_file_path}")
            return
        except Exception as e:
            logging.error(f"Error reading Markdown file {self.md_file_path}: {e}")
            return

        sections = self.extract_sections_from_md(md_content)
        if not sections:
            logging.warning("No sections found in the Markdown file.")
            # Fallback: treat the whole file as one section if no '##' headers
            # This part needs to align with how the original script would behave if no '##' found.
            # The original `extract_sections` would return empty, and `write_sections` would do nothing.
            # To maintain exact functionality, if no sections, we do nothing further with section writing.
            if not re.search(r'^##\s+', md_content, flags=re.MULTILINE):
                logging.info("No '##' sections found. If the entire file should be one section, this needs specific handling.")
                # To replicate original: if no '##' sections, then no .tex files are written by write_sections.
                # If the intent was to process the whole file if no '##', that logic would need to be added here.
                # For now, sticking to original behavior: no '##' means no section files.
                print(f"Processed 0 sections (no '##' headers found).")
                return

        for sec_data in sections:
            out_path = os.path.join(self.sections_dir, sec_data['filename'])
            latex_content = self.convert_section_content_to_latex(sec_data['content'])
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
                logging.info(f"Wrote {out_path} ({len(latex_content)} chars)")
            except Exception as e:
                logging.error(f"Error writing LaTeX file {out_path}: {e}")
        
        print(f"Processed {len(sections)} sections.")

# Main execution block (similar to original script)
if __name__ == "__main__":
    # These paths are relative to where the script is run, typically LaTeX_withTikZ_Tutorial
    MD_FILE_DEFAULT = os.path.join("..", "wip", "experiments", "GASing_Arithmetic.md")
    SECTIONS_DIR_DEFAULT = "sections"
    IMAGES_DIR_DEFAULT = "images" # Relative to SECTIONS_DIR_DEFAULT or script CWD?
                                 # Original script implies IMAGES_DIR is relative to script's CWD.

    # Check if MD_FILE_DEFAULT exists from the typical execution directory
    # (e.g. LaTeX_withTikZ_Tutorial)
    if not os.path.exists(MD_FILE_DEFAULT):
        # Fallback if script is run from a different CWD, try to locate relative to script itself
        script_dir = os.path.dirname(os.path.abspath(__file__))
        MD_FILE_DEFAULT = os.path.join(script_dir, "..", "wip", "experiments", "GASing_Arithmetic.md")
        SECTIONS_DIR_DEFAULT = os.path.join(script_dir, "sections")
        IMAGES_DIR_DEFAULT = os.path.join(script_dir, "images")
        # The base_output_dir for image paths also needs to be relative to where main.tex is expected
        # This might need adjustment if the script's CWD assumption changes.

    converter = MarkdownToLatexConverter(
        md_file_path=MD_FILE_DEFAULT,
        sections_dir=SECTIONS_DIR_DEFAULT,
        images_dir=IMAGES_DIR_DEFAULT
    )
    converter.process_and_write_sections()