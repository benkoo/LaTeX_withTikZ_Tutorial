import os
import re
import glob

# Paths
MD_FILE = os.path.join("..", "wip", "experiments", "GASing_Arithmetic.md")
SECTIONS_DIR = "sections"
IMAGES_DIR = "images"

# Ensure images directory exists
os.makedirs(IMAGES_DIR, exist_ok=True)

# Helper: Convert a section title to a normalized filename
def section_title_to_filename(title):
    # Remove leading numbers, dots, spaces, and special characters
    title = re.sub(r"^\d+[. ]*", "", title.strip())
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = re.sub(r"_+", "_", title).strip('_')
    return f"{title}.tex"

# Fix section numbering like '2.0.1' -> '2.1'
def fix_section_numbering(text):
    return re.sub(r'(\d+)\.0\.(\d+)', r'\1.\2', text)

# Markdown to LaTeX conversion (basic)
def process_inline_code(code_text):
    """Process inline code text to properly handle LaTeX special characters"""
    # First handle already escaped sequences - protect them from double escaping
    escaped_sequences = {}
    
    # Preserve already escaped sequences
    def preserve_escapes(match):
        placeholder = f"__ESCAPED_SEQ_{len(escaped_sequences)}__"
        escaped_sequences[placeholder] = match.group(0)
        return placeholder
    
    # Store all existing escaped sequences
    code_text = re.sub(r'\\([\\%&$#_{}^~])', preserve_escapes, code_text)
    
    # Handle full math expressions with parentheses
    # Detect mathematical expressions with carets and wrap them entirely in math mode
    math_patterns = [
        # Pattern: (n^k - b) - capture and convert to proper math mode
        (r'\(([^\)]+?)\^([^\)]+?)\s*-\s*([^\)]+?)\)', r'$(\1^{\2} - \3)$'),
        # Simple variable with exponent: n^k
        (r'(\w+)\^(\w+)', r'$\1^{\2}$'),
        # Variable with subscript: a_i
        (r'(\w+)_(\w+)', r'$\1_{\2}$'),
    ]
    
    for pattern, replacement in math_patterns:
        code_text = re.sub(pattern, replacement, code_text)
    
    # For any remaining carets that aren't in math expressions, escape them
    # Avoid using textasciicircum inside math mode
    code_text = re.sub(r'\^(?![{\w])', r'\\^{}', code_text)
    
    # Handle special LaTeX characters that need escaping outside math mode
    # Be careful not to escape inside existing math expressions
    def escape_outside_math(text):
        # Split by math delimiters $...$
        parts = re.split(r'(\$[^\$]*\$)', text)
        result = []
        
        for i, part in enumerate(parts):
            # Skip math parts (odd indices after splitting by capturing group)
            if i % 2 == 1:  
                result.append(part)
            else:
                # For text parts, escape special characters
                escaped_part = part
                for char in ['%', '&', '#', '_', '~']:
                    escaped_part = escaped_part.replace(char, f'\\{char}')
                result.append(escaped_part)
                
        return ''.join(result)
    
    # Apply character escaping outside math regions
    code_text = escape_outside_math(code_text)
    
    # Restore preserved escaped sequences
    for placeholder, original in escaped_sequences.items():
        code_text = code_text.replace(placeholder, original)
    
    # Return the final text inside \texttt{}
    return f'\\texttt{{{code_text}}}'

def clean_header_lines(text):
    """Special function to handle all header edge cases"""
    # First, normalize all potential header lines (with various combinations of backslashes and hashes)
    
    # 1. Handle lines starting with backslash + hashes (e.g., \### or \##)
    text = re.sub(r'^\\+(#+)\s+(.+)$', r'\1 \2', text, flags=re.MULTILINE)
    
    # 2. Handle the specific case of '\## ##' pattern (backslash-hash-hash space hash-hash)
    text = re.sub(r'^\\##\s+##\s+(.+)$', r'#### \1', text, flags=re.MULTILINE)
    
    # 3. Handle any line starting with multiple hash marks
    text = re.sub(r'^(#+)\s+(.+)$', 
                 lambda m: '#' * len(m.group(1)) + ' ' + m.group(2), 
                 text, flags=re.MULTILINE)
    
    # 4. Remove any remaining backslashes before hash marks
    text = re.sub(r'^\\(#+\s+.+)$', r'\1', text, flags=re.MULTILINE)
    
    return text

def find_image_file(image_name):
    """Find an image file in the images directory, case-insensitive"""
    if not os.path.exists(IMAGES_DIR):
        return None
        
    # Get all files in the images directory
    image_files = glob.glob(os.path.join(IMAGES_DIR, '*'))
    
    # Try exact match first
    for file_path in image_files:
        if os.path.basename(file_path) == image_name:
            return file_path
    
    # Try case-insensitive match
    image_name_lower = image_name.lower()
    for file_path in image_files:
        if os.path.basename(file_path).lower() == image_name_lower:
            return file_path
    
    return None

def process_image_links(text):
    """Process standard Markdown image links: ![Label](image.png)"""
    def replace_image(match):
        # Get the full match, label, and image path
        full_match = match.group(0)
        label = match.group(1).strip()
        image_name = match.group(2).strip()
        
        if not image_name:
            return full_match
            
        # Find the image file
        image_file = find_image_file(image_name)
        
        if not image_file:
            print(f"Warning: Image '{image_name}' not found in {IMAGES_DIR}")
            return full_match
            
        try:
            # Get the relative path from the LaTeX output directory to the image
            output_dir = os.path.dirname(os.path.abspath('main.tex'))
            rel_path = os.path.relpath(
                os.path.abspath(image_file),
                output_dir
            )
            
            # Normalize path for LaTeX (forward slashes, no backslashes)
            rel_path = rel_path.replace('\\', '/')
            
            # Remove the .tex extension if present (for the label)
            base_name = os.path.splitext(os.path.basename(image_name))[0]
            
            # Create a very simple label - alphanumeric only, no special characters or underscores
            # This ensures maximum compatibility with LaTeX's reference system
            safe_label = re.sub(r'[^a-zA-Z0-9]', '', base_name).lower()
            
            # Use the label as the caption if provided, otherwise use filename
            caption = label if label else base_name.replace('_', ' ').title()
            
            # Ensure the path is properly formatted for LaTeX
            # - Replace backslashes with forward slashes
            # - Don't escape underscores in the path (they're valid in filenames)
            # - Remove any double slashes that might have been created
            rel_path = rel_path.replace('\\', '/').replace('//', '/')
            
            # Create LaTeX figure environment with correct label formatting
            # Ensure labels are safe for LaTeX - alphanumeric only, no special characters
            # Use standard LaTeX naming conventions for labels
            return (
                '\n\\begin{figure}[H]\n'
                '  \\centering\n'
                f'  \\includegraphics[width=\\linewidth]{{{rel_path}}}\n'
                f'  \\caption{{{caption}}}\n'
                f'  \\label{{fig:{safe_label}}}\n'
                '\\end{figure}\n'
            )
        except Exception as e:
            print(f"Error processing image {image_name}: {str(e)}")
            return full_match
    
    # Find all patterns like ![Label](image.png) with optional spaces
    pattern = r'!\s*\[([^\]]*)\]\s*\(\s*([^)\s]+)\s*\)'
    return re.sub(pattern, replace_image, text, flags=re.MULTILINE)


def strip_section_numbering(header_text):
    """Remove numerical prefixes from section headers (e.g., '3.2 Introduction' becomes 'Introduction')"""
    # Pattern to match numerical prefixes like '3.', '3.2.1' at the beginning of a string
    # followed by a space and the actual section title
    return re.sub(r'^(\d+(\.\d+)*)\s+(.+)$', r'\3', header_text)

def md_to_latex(md):
    # Preprocessing: Clean up all header-related patterns
    md = clean_header_lines(md)
    
    # Process image links before other markdown processing
    md = process_image_links(md)
    
    # Split into code and non-code segments
    segments = []
    last_end = 0
    
    # Extract code blocks with language info
    for match in re.finditer(r'```(?:([a-zA-Z]*))?\s*\n([\s\S]*?)```', md):
        # Non-code segment before this code block
        if match.start() > last_end:
            segments.append(('text', md[last_end:match.start()]))
        
        # Get language (default to Python if none specified)
        lang = match.group(1) or 'Python'
        
        # Get code content
        code = match.group(2)
        
        # Store code with language info
        segments.append(('code', code, lang))
        last_end = match.end()
        
    # Remainder after last code block
    if last_end < len(md):
        segments.append(('text', md[last_end:]))

    latex_parts = []
    for item in segments:
        typ = item[0]
        
        if typ == 'code':
            # Unpack code and language
            seg, lang = item[1], item[2]
            
            # Determine appropriate language for listings
            listings_lang = {
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
            }.get(lang.lower(), 'Python')  # Default to Python if language not recognized
            
            # Extract algorithm name/caption from the first line if it looks like a function definition
            caption = ''
            if seg.strip().startswith(('def ', 'function ', 'class ', '# ')):
                first_line = seg.strip().split('\n')[0].strip()
                # Remove leading 'def ' or 'function ' or 'class '
                for prefix in ['def ', 'function ', 'class ', '# ']:
                    if first_line.startswith(prefix):
                        caption = first_line[len(prefix):].split('(')[0].strip() + ' Algorithm'
                        break
            
            # Use a simpler LaTeX listings format that exactly matches the appendix
            if caption:
                # Escape underscores in caption to avoid LaTeX math mode errors
                escaped_caption = caption.replace('_', '\\_')
                caption_text = f",caption={{{escaped_caption}}}"
            else:
                caption_text = ""
                
            # Use exact format from appendix.tex that we know works in LaTeX
            tex_code = f"\\begin{{lstlisting}}[language={listings_lang}{caption_text}]\n{seg.rstrip()}\n\\end{{lstlisting}}"
            latex_parts.append(tex_code)
        else:
            # Get the text content
            seg = item[1]
            
            # Escape underscores outside code blocks
            seg = re.sub(r'(?<!\\)_', r'\\_', seg)
            # Convert headers to LaTeX section commands
            # Use a consistent approach for all header levels with defensive programming
            
            # First normalize any headers that might have unusual patterns
            seg = clean_header_lines(seg)
            
            # Now convert using the normalized headers
            # Order matters! Process deeper header levels first (###) before shallower ones (#)
            # Also strip section numbering
            seg = re.sub(r'^\s*#{3,}\s+(.+)$', 
                      lambda m: '\\paragraph{' + strip_section_numbering(m.group(1)) + '}', 
                      seg, flags=re.MULTILINE)  # ### or more (now paragraph with no numbering)
            seg = re.sub(r'^\s*#{2}\s+(.+)$', 
                      lambda m: '\\subsection{' + strip_section_numbering(m.group(1)) + '}', 
                      seg, flags=re.MULTILINE)  # ##
            seg = re.sub(r'^\s*#{1}\s+(.+)$', 
                      lambda m: '\\section{' + strip_section_numbering(m.group(1)) + '}', 
                      seg, flags=re.MULTILINE)  # #
            
            # For any headers that might have been missed with unusual patterns
            # (defensive approach for anything remaining)
            seg = re.sub(r'^\s*\\*#+\s+(.+)$', 
                        lambda m: '\\' + ('sub' * min(2, m.group(0).count('#')-1)) + 'section{' + 
                                strip_section_numbering(m.group(1).strip()) + '}', 
                        seg, flags=re.MULTILINE)
            
            # 3. Escape any stray # at the start of a line (not already converted)
            seg = re.sub(r'^(?P<pre>[^\\].*?)#', lambda m: m.group('pre') + r'\#', seg, flags=re.MULTILINE)
            
            # 4. Clean up any malformed LaTeX section commands
            # Ensure section commands have proper closing braces on the same line
            for cmd in ['section', 'subsection', 'subsubsection']:
                # Make sure each section command has a closing brace on the same line
                seg = re.sub(r'^(\\' + cmd + r'\{[^}]*?)$', r'\1}', seg, flags=re.MULTILINE)
                
                # Fix any cases where a section command doesn't have a closing brace
                # Pattern matches a section command that doesn't have a closing brace
                pattern = r'^(\\' + cmd + r'\{[^}]*[^}\n])$'
                seg = re.sub(pattern, r'\1}', seg, flags=re.MULTILINE)
                
                # Remove any standalone closing braces at the start of lines
                # (these are likely leftover from previous processing)
                seg = re.sub(r'^}\s*$', '', seg, flags=re.MULTILINE)
            # Convert [[text_content]] to \textbf{\textit{text_content}} for bold italics
            seg = re.sub(r'\[\[([^\]]+)\]\]', r'\\textbf{\\textit{\1}}', seg)
            
            # Process dash bullet points with more precise matching
            # First handle the case with label: description format
            seg = re.sub(r'(^|\n)[ \t]*-[ \t]*([^\n:]+):[ \t]*(.+)', r'\1\n\\noindent\\textbf{\2:} \3\n', seg)
            
            # Then handle regular dash bullet points (but avoid matching ones already processed)
            seg = re.sub(r'(^|\n)[ \t]*-[ \t]*(?!\\noindent)(.+)', r'\1\n\\noindent \2\n', seg)
            
            # Convert special bullet points with labeled items first
            # Pattern: "* Label: Description" with text following
            labeled_pattern = r'(^|\n)\s*\*\s+([^\n:]+):\s*([^\n]+)(?:\n+([^\n*][^\n]+(?:\n+(?!\s*\*\s+)[^\n]+)*))?'
            
            def process_labeled_bullets(match):
                prefix = match.group(1)
                label = match.group(2).strip()
                description = match.group(3).strip()
                
                # Check if there's following content
                following_content = ""
                if match.group(4):
                    content_lines = []
                    for line in match.group(4).strip().split('\n'):
                        content_lines.append(line.strip())
                    # Use simple indentation for content following bullet points
                    content_text = ' '.join(content_lines)
                    following_content = f"\n\n\\vspace{{0.5em}}\n\\noindent\\hspace{{2em}}{content_text}\n\\vspace{{0.5em}}\n"
                
                return f"{prefix}\\begin{{itemize}}\n\\item \\textbf{{{label}:}} {description}{following_content}\n\\end{{itemize}}\n"
            
            # Process labeled bullets
            seg = re.sub(labeled_pattern, process_labeled_bullets, seg, flags=re.DOTALL)
            
            # Now handle regular bullet points with content following
            regular_pattern = r'(^|\n)\s*\*\s+([^\n:][^\n]*)(?:\n+([^\n*][^\n]+(?:\n+(?!\s*\*\s+)[^\n]+)*))?'
            
            def process_regular_bullets(match):
                prefix = match.group(1)
                bullet_text = match.group(2).strip()
                
                # Check if there's following content
                following_content = ""
                if match.group(3):
                    content_lines = []
                    for line in match.group(3).strip().split('\n'):
                        content_lines.append(line.strip())
                    # Use simple indentation for content following bullet points
                    content_text = ' '.join(content_lines)
                    following_content = f"\n\n\\vspace{{0.5em}}\n\\noindent\\hspace{{2em}}{content_text}\n\\vspace{{0.5em}}\n"
                
                return f"{prefix}\\begin{{itemize}}\n\\item {bullet_text}{following_content}\n\\end{{itemize}}\n"
            
            # Process regular bullets
            seg = re.sub(regular_pattern, process_regular_bullets, seg, flags=re.DOTALL)
            
            # We'll not add package declarations to section files as they can only go in the preamble
            # Instead, we need to modify our approach to not rely on the enumitem package
            # Convert description environments to use standard LaTeX formatting
            
            # Now handle regular bullet points that don't have additional paragraphs
            simple_bullet_pattern = r'(^|\n)\s*\*\s+([^\n]+)(?!\n+(?!\s*\*\s+)[^\n]+)'
            
            def process_simple_bullet(match):
                prefix = match.group(1)
                bullet = match.group(2).strip()
                
                # If bullet has a label with colon, format it specially
                if ':' in bullet and not bullet.startswith('\\'):
                    label, desc = bullet.split(':', 1)
                    return f"{prefix}\\begin{{itemize}}\n\\item \\textbf{{{label.strip()}:}} {desc.strip()}\n\\end{{itemize}}\n"
                
                # Regular bullet point
                return f"{prefix}\\begin{{itemize}}\n\\item {bullet}\n\\end{{itemize}}\n"
            
            # Process simple bullet points
            seg = re.sub(simple_bullet_pattern, process_simple_bullet, seg, flags=re.DOTALL)
            
            # No need to add packages in the middle of content
            # Convert bold and italics
            seg = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', seg)
            seg = re.sub(r'\*(.+?)\*', r'\\emph{\1}', seg)
            
            # Handle <mcfile> tags with custom formatting to avoid overly long paths
            seg = re.sub(r'<mcfile\s+name="([^"]+)"\s+path="([^"]+)"></mcfile>', 
                       lambda m: f'\\textit{{\\href{{file://\{m.group(2)}}}{{{m.group(1)}}}}}', 
                       seg)
            # Inline code - handle special LaTeX characters including caret (^) which needs math mode
            seg = re.sub(r'`([^`]+)`', lambda m: process_inline_code(m.group(1)), seg)
            latex_parts.append(seg)
    return ''.join(latex_parts)

# Extract all top-level sections (##) and their content
def extract_sections(md):
    # Find all top-level sections (## ...), capturing their content until the next top-level section
    section_pattern = r'^##\s+(.+?)\n([\s\S]*?)(?=^##\s+|\Z)'
    matches = re.finditer(section_pattern, md, flags=re.MULTILINE)
    sections = {}
    for match in matches:
        title = match.group(1).strip()
        content = match.group(2).strip()
        filename = section_title_to_filename(title)
        sections[filename] = {'title': title, 'content': content}
    return sections

# Write each section to a .tex file
def write_sections(sections):
    if not os.path.exists(SECTIONS_DIR):
        os.makedirs(SECTIONS_DIR)
    for filename, sec in sections.items():
        out_path = os.path.join(SECTIONS_DIR, filename)
        latex = md_to_latex(sec['content'])
        with open(out_path, 'w') as f:
            f.write(latex)
        print(f"Wrote {out_path} ({len(latex)} chars)")

if __name__ == "__main__":
    with open(MD_FILE, 'r') as f:
        md = f.read()
    sections = extract_sections(md)
    write_sections(sections)
    print(f"Processed {len(sections)} sections.")

# Extract main sections and their subsections
def extract_sections(content):
    sections = {}
    
    # Special extraction for Computational Advantages section with all its subsections
    comp_adv_pattern = r'## 5\. Computational Advantages\s*\n([\s\S]*?)(?=## 6\.)'    
    comp_adv_match = re.search(comp_adv_pattern, content)
    if comp_adv_match:
        full_content = comp_adv_match.group(1).strip()
        sections['computational advantages'] = {
            'content': full_content,
            'filename': 'computational_advantages.tex'
        }
        print(f"Found complete computational advantages section with {len(full_content)} characters")
    
    # For remaining sections, use the standard pattern

    sections = {}
    
    # Dynamically extract all top-level sections (## ...) and their content
    section_pattern = r'^##\s+(.+?)\n([\s\S]*?)(?=^##\s+|\Z)'
    matches = re.finditer(section_pattern, content, flags=re.MULTILINE)
    sections = {}
    for match in matches:
        title = match.group(1).strip()
        content = match.group(2).strip()
        filename = section_title_to_filename(title)
        sections[filename] = {
            'title': title,
            'content': content,
            'filename': filename
        }
        print(f"Found section: {title} (filename: {filename}, {len(content)} chars)")
    
    return sections

# Process sections and write to files
def process_sections(sections):
    for section_title, section_data in sections.items():
        content = section_data['content']
        filename = section_data['filename']
        
        tex_path = os.path.join(SECTIONS_DIR, filename)
        
        # Create backup of existing file
        if os.path.exists(tex_path):
            backup_path = f"{tex_path}.bak"
            try:
                with open(tex_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            except Exception as e:
                print(f"Warning: Failed to create backup of {filename}: {e}")
        
        # Convert markdown to LaTeX
        latex_content = md_to_latex(content)
        
        # Write updated content
        with open(tex_path, 'w') as f:
            f.write(latex_content + '\n')
            
        print(f"Updated {filename} from section '{section_title}'")

# Read markdown file
with open(MD_FILE, 'r') as f:
    content = f.read()

# Extract sections from Markdown content
sections = extract_sections(content)

# Process and write sections to LaTeX files
process_sections(sections)
