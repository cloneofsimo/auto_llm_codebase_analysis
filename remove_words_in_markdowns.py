import os

def process_markdown_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                content = content.replace('<|im_end|>', '')
                
                # Write modified content back to file
                with open(file_path, 'w') as f:
                    f.write(content)

folder_path = ""
process_markdown_files(folder_path)
