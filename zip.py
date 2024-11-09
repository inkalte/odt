import zipfile
import os

with zipfile.ZipFile('./PyOnl.zip', mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:
    for folder, sub_folder, files in os.walk('./'):
        if folder.startswith('./.idea') or folder.startswith('./venv') or folder.startswith('./__pycache__'):
            continue

        for file in files:
            if file == 'PyOnl.zip':
                continue
            file_path = os.path.join(folder, file)
            print(file_path)
            zip_file.write(file_path)
