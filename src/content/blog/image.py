import os
import re
from pathlib import Path

def convert_img_tags(content):
    # Pattern to match <img> tags with src, alt, and width attributes
    pattern = re.compile(r'<img\s+src="([^"]+)"\s+alt="([^"]*)"(?:\s+width="([^"]*)")?\s*/>')
    
    def replacement(match):
        src = match.group(1)
        alt = match.group(2)
        # Convert src to URL-encoded format if needed
        encoded_src = src.replace(' ', '%20')
        return f'![{alt}]({encoded_src})'
    
    return pattern.sub(replacement, content)

def process_md_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'index.md':
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = convert_img_tags(content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'Updated: {filepath}')

if __name__ == '__main__':
    blog_dir = input('Enter the path to your blog directory: ')
    if os.path.isdir(blog_dir):
        process_md_files(blog_dir)
        print('Image tag conversion complete!')
    else:
        print('Invalid directory path. Please try again.')
