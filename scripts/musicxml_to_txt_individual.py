# Script to copy each .musicxml file to a .txt file in the same directory
import os

musicxml_dir = os.path.join(os.path.dirname(__file__), '..', 'musicxml')

for filename in os.listdir(musicxml_dir):
    if filename.endswith('.musicxml'):
        src_path = os.path.join(musicxml_dir, filename)
        dst_filename = filename.rsplit('.musicxml', 1)[0] + '.txt'
        dst_path = os.path.join(musicxml_dir, dst_filename)
        with open(src_path, 'r', encoding='utf-8') as src_file:
            with open(dst_path, 'w', encoding='utf-8') as dst_file:
                dst_file.write(src_file.read())
print('All .musicxml files have been copied to .txt files in the same directory.')
