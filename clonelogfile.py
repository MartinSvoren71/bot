import shutil

    def clone_file(source_path, destination_path, force_overwrite=False):
try:
    if force_overwrite:
        shutil.copy2(source_path, destination_path)
    else:
        shutil.copy2(source_path, destination_path + '/' + os.path.basename(source_path))
        print("File cloned successfully!")
except Exception as e:
    print(f"Error: {e}")
        

        

