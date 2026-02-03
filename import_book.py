import os
import re
import shutil

def import_book(file_path):
    print(f"Importing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine book name from filename
    book_name = os.path.basename(file_path).replace('.txt', '').replace('.md', '').replace('_', ' ').title()
    output_dir = os.path.join('book_content', book_name)
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Split content by Page markers
    # Supports: [Page 1], # Page 1, Page 1
    pages = re.split(r'(?:^|\n)(?:\[Page\s+(\d+)\]|#\s*Page\s+(\d+)|Page\s+(\d+))', content, flags=re.IGNORECASE)
    
    # If no pages found, treat as one big page
    if len(pages) < 2:
        print("No page markers found (e.g. '[Page 1]'). Importing as single chapter.")
        with open(os.path.join(output_dir, 'page-1.md'), 'w', encoding='utf-8') as f:
            f.write("# " + book_name + "\n\n" + content)
        return

    current_page_num = 0
    
    # pages[0] is intro text before first page marker
    if pages[0].strip():
        with open(os.path.join(output_dir, 'page-000-intro.md'), 'w', encoding='utf-8') as f:
            f.write(pages[0].strip())

    # Iterate through split result
    # Format is: [text, page_num, text, page_num, text...] due to capture groups
    # Actually, re.split with multiple capture groups is tricky. 
    # Let's use a simpler regex iterator.
    
    page_matches = list(re.finditer(r'(?:^|\n)(?:\[Page\s+(\d+)\]|#\s*Page\s+(\d+)|Page\s+(\d+))', content, flags=re.IGNORECASE))
    
    if not page_matches:
         with open(os.path.join(output_dir, 'page-1.md'), 'w', encoding='utf-8') as f:
            f.write("# " + book_name + "\n\n" + content)
         return

    last_pos = 0
    for i, match in enumerate(page_matches):
        # Determine actual page number from the groups
        page_num = next(g for g in match.groups() if g is not None)
        
        # Determine start and end of this page's content
        start_pos = match.end()
        end_pos = page_matches[i+1].start() if i + 1 < len(page_matches) else len(content)
        
        page_text = content[start_pos:end_pos].strip()
        
        # Add Header if missing
        if not page_text.startswith('#'):
            page_text = f"# Page {page_num}\n\n{page_text}"

        filename = f"page-{int(page_num):03d}.md"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(page_text)
            
        print(f"Generated {filename}")

    print(f"Successfully imported '{book_name}' with {len(page_matches)} pages.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python import_book.py <path_to_book_file>")
    else:
        import_book(sys.argv[1])
