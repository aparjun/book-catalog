import os
import re
import markdown
import shutil
from jinja2 import Environment, FileSystemLoader

# Configuration
CONTENT_DIR = 'book_content'
OUTPUT_DIR = 'books'
TEMPLATE_DIR = 'templates'
ASSETS_DIR = 'assets'

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text).strip('-')

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def build_site():
    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    index_template = env.get_template('index.html')
    book_template = env.get_template('book.html')

    books = []

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Process each book
    if os.path.exists(CONTENT_DIR):
        for book_name in os.listdir(CONTENT_DIR):
            book_path = os.path.join(CONTENT_DIR, book_name)
            if not os.path.isdir(book_path):
                continue
            
            print(f"Processing book: {book_name}")
            
            # Create book output dir
            book_slug = slugify(book_name)
            book_out_dir = os.path.join(OUTPUT_DIR, book_slug)
            if not os.path.exists(book_out_dir):
                os.makedirs(book_out_dir)

            # Get pages
            files = [f for f in os.listdir(book_path) if f.endswith('.md')]
            files.sort(key=natural_sort_key)
            
            toc = []
            page_data = []

            # First pass: Build TOC and metadata
            for filename in files:
                filepath = os.path.join(book_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract title from first h1 or filename
                lines = content.split('\n')
                title = filename.replace('.md', '').replace('-', ' ').title()
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                html_filename = filename.replace('.md', '.html')
                toc.append({'title': title, 'filename': html_filename})
                
                # Convert MD to HTML 
                html_content = markdown.markdown(content)
                page_data.append({
                    'filename': html_filename,
                    'title': title,
                    'content': html_content
                })

            # Second pass: Write files with nav links
            for i, page in enumerate(page_data):
                prev_page = page_data[i-1]['filename'] if i > 0 else None
                next_page = page_data[i+1]['filename'] if i < len(page_data) - 1 else None
                
                output = book_template.render(
                    book_title=book_name,
                    page_title=page['title'],
                    content=page['content'],
                    toc=toc,
                    current_filename=page['filename'],
                    prev_page=prev_page,
                    next_page=next_page
                )
                
                with open(os.path.join(book_out_dir, page['filename']), 'w', encoding='utf-8') as f:
                    f.write(output)

            books.append({
                'title': book_name, 
                'slug': book_slug,
                'pages': toc
            })

    # Build Index
    index_html = index_template.render(books=books)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
        
    print("Build complete!")

if __name__ == "__main__":
    build_site()
