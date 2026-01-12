#!/usr/bin/env python3
import os
import zipfile

def create_zip(zip_filename, source_dir):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

if __name__ == "__main__":
    create_zip('/tmp/test_real_component.zip', '/tmp/test_real_component')
    print("Zip file created successfully!")
