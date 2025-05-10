#!/usr/bin/env python3
"""
Markdown Structure Validator for GASing Documentation

This script validates Markdown files for proper section and subsection structure,
ensuring they're ready for LaTeX transcription. It performs multiple checks:
1. Header hierarchy validation (no skipped levels, proper nesting)
2. Header formatting consistency
3. Identification of problematic patterns (escaped headers, unbalanced backticks)
4. Automatic cleanup of known issues

Usage:
    python3 validate_markdown_structure.py [markdown_file]
"""

import os
import re
import sys
from collections import defaultdict

# Default path (can be overridden with command line arg)
DEFAULT_MD_FILE = os.path.join("..", "wip", "experiments", "GASing_Arithemtic.md")
CLEANED_SUFFIX = ".cleaned.md"

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def basic_cleanup(content):
    """
    Performs basic cleanup on Markdown content without structural validation.
    Returns the cleaned content.
    """
    cleaned_content = content
    
    # Fix escaped headers
    cleaned_content = re.sub(r'^\\+(#+\s+)', r'\1', cleaned_content, flags=re.MULTILINE)
    
    # Ensure proper spacing after header markers
    cleaned_content = re.sub(r'^(#+)([^\s])', r'\1 \2', cleaned_content, flags=re.MULTILINE)
    
    # Convert any \# (escaped hash) at beginning of lines to proper heading
    # This handles the ambiguous case of "\# Text" which might be confused with "\\# Text"
    cleaned_content = re.sub(r'^\\#', r'#', cleaned_content, flags=re.MULTILINE)
    
    # Ensure all codeblocks are properly formatted (three backticks, not fewer)
    cleaned_content = re.sub(r'^``([^`])', r'```\1', cleaned_content, flags=re.MULTILINE)
    
    return cleaned_content

def validate_markdown_structure(md_file):
    """
    Validates a Markdown file for proper structure and formatting.
    Returns the cleaned Markdown content if validation passes.
    """
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Make a copy of content for validation (we'll return the clean version later)
    original_content = content
    
    print(f"Validating structure of {md_file}...")
    
    # Convert any escaped headers (e.g., \#### -> ####) for validation
    content = re.sub(r'^\\+(#+\s+)', r'\1', content, flags=re.MULTILINE)
    
    # 1. Check for proper header hierarchy
    header_levels = []
    header_pattern = re.compile(r'^(#+)\s+(.+?)$', re.MULTILINE)
    headers = header_pattern.findall(content)
    
    if not headers:
        raise ValidationError("No headers found in the document")
    
    print(f"Found {len(headers)} headers in the document.")
    
    # Process all headers
    for i, (hashes, title) in enumerate(headers):
        level = len(hashes)
        
        # First header should be level 1 or 2 (# or ##)
        if i == 0 and level > 2:
            raise ValidationError(f"First header should be # or ##, found {'#' * level} {title}")
        
        # Check for skipped levels (e.g., # -> ###), but be smart about numeric sections
        if i > 0:
            prev_level = len(headers[i-1][0])
            prev_title = headers[i-1][1].strip()
            curr_title = title.strip()
            
            # Extract section numbers if present (e.g., "3." from "3. Introduction")
            prev_section_match = re.match(r'^(\d+(\.\d+)*)\s', prev_title)
            curr_section_match = re.match(r'^(\d+(\.\d+)*)\s', curr_title)
            
            # If both headers have section numbers, check if they follow correct hierarchy
            if prev_section_match and curr_section_match:
                prev_section = prev_section_match.group(1)
                curr_section = curr_section_match.group(1)
                
                # If current section is a subsection of previous (e.g., 3.1 after 3), 
                # allow level jump by checking if curr starts with prev
                if curr_section.startswith(prev_section + ".") or curr_section == prev_section:
                    # This is a valid subsection relationship
                    pass
                elif level > prev_level + 1:
                    # Only raise error if sections don't have numeric relationship AND level jumps
                    raise ValidationError(
                        f"Header level jumps from {prev_level} to {level} at: {'#' * level} {title}"
                    )
            elif level > prev_level + 1:
                # For headers without section numbers, enforce strict hierarchy
                raise ValidationError(
                    f"Header level jumps from {prev_level} to {level} at: {'#' * level} {title}"
                )
        
        header_levels.append(level)
    
    # 2. Check for consistent header formatting
    section_titles = defaultdict(list)
    for hashes, title in headers:
        level = len(hashes)
        section_titles[level].append(title.strip())
    
    # Check for duplicate section titles at the same level
    for level, titles in section_titles.items():
        titles_set = set(titles)
        if len(titles) != len(titles_set):
            duplicates = [t for t in titles if titles.count(t) > 1]
            raise ValidationError(
                f"Duplicate section titles at level {level}: {', '.join(set(duplicates))}"
            )
    
    # 3. Check for problematic patterns
    
    # 3.1 Check for any remaining escaped header patterns
    escaped_headers = re.findall(r'^\\#+\s+(.+?)$', original_content, re.MULTILINE)
    if escaped_headers:
        print(f"Warning: Found {len(escaped_headers)} escaped headers (e.g., \\### {escaped_headers[0]})")
        print("These will be automatically fixed.")
    
    # 3.2 Check for inline code within headers (potential LaTeX issues)
    for hashes, title in headers:
        if '`' in title and title.count('`') % 2 != 0:
            raise ValidationError(f"Unbalanced backticks in header: {hashes} {title}")
    
    # 3.3 Check for headers that end with a colon (typically not LaTeX-friendly)
    colon_headers = []
    for hashes, title in headers:
        if title.strip().endswith(':'):
            colon_headers.append(f"{hashes} {title}")
    
    if colon_headers:
        print("Warning: The following headers end with colons (may cause LaTeX formatting issues):")
        for h in colon_headers[:3]:  # Show at most 3 examples
            print(f"  - {h}")
        if len(colon_headers) > 3:
            print(f"  - ... and {len(colon_headers) - 3} more")
    
    # If all checks pass, clean up any problematic patterns
    cleaned_content = original_content
    
    # Fix escaped headers
    cleaned_content = re.sub(r'^\\+(#+\s+)', r'\1', cleaned_content, flags=re.MULTILINE)
    
    # Ensure proper spacing after header markers
    cleaned_content = re.sub(r'^(#+)([^\s])', r'\1 \2', cleaned_content, flags=re.MULTILINE)
    
    # Convert any \# (escaped hash) at beginning of lines to proper heading
    # This handles the ambiguous case of "\# Text" which might be confused with "\\# Text"
    cleaned_content = re.sub(r'^\\#', r'#', cleaned_content, flags=re.MULTILINE)
    
    # Ensure all codeblocks are properly formatted (three backticks, not fewer)
    cleaned_content = re.sub(r'^``([^`])', r'```\1', cleaned_content, flags=re.MULTILINE)
    
    return cleaned_content

def main():
    """Main function to validate Markdown files."""
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Validate Markdown structure for LaTeX conversion')
    parser.add_argument('file', nargs='?', default=DEFAULT_MD_FILE, help='Path to Markdown file to validate')
    parser.add_argument('--skip-hierarchy-check', action='store_true', help='Skip header hierarchy validation (level jumps)')
    parser.add_argument('--skip-all-validation', action='store_true', help='Skip all validation and just clean the file')
    parser.add_argument('--force', action='store_true', help='Continue processing despite validation errors')
    
    args = parser.parse_args()
    md_file = args.file
    
    if not os.path.exists(md_file):
        print(f"Error: File not found: {md_file}")
        sys.exit(1)
    
    # Read the file content
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Variable to track if validation passed
    validation_passed = True
    cleaned_content = content
    
    try:
        if not args.skip_all_validation:
            # Replace the full validation with targeted validation functions
            if not args.skip_hierarchy_check:
                # Only check header hierarchy if not skipped
                print("Checking header hierarchy...")
                cleaned_content = validate_markdown_structure(md_file)
            else:
                print("Skipping header hierarchy check as requested.")
                # Still do basic cleanup without validation
                cleaned_content = basic_cleanup(content)
        else:
            print("Skipping all validation as requested.")
            # Just do basic cleanup
            cleaned_content = basic_cleanup(content)
            
        print(f"✅ Processing completed for {md_file}")
    except ValidationError as e:
        validation_passed = False
        print(f"❌ Validation failed: {e}")
        if not args.force:
            sys.exit(1)
        else:
            print("Continuing despite validation errors (--force flag set)")
            # Apply basic cleanup even when validation fails
            cleaned_content = basic_cleanup(content)
    
    # Write cleaned content regardless of validation status if force flag is set
    base, ext = os.path.splitext(md_file)
    temp_file = base + CLEANED_SUFFIX
    with open(temp_file, 'w') as f:
        f.write(cleaned_content)
    
    print(f"✅ Cleaned content written to {temp_file}")
    print("✅ Ready for LaTeX transcription")
    
    # Return the path to the cleaned file
    print(temp_file)
    sys.exit(0 if validation_passed or args.force else 1)

if __name__ == "__main__":
    main()
