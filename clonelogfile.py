import shutil

def clone_file(source_path, destination_path, force_overwrite=False):
    if force_overwrite or not os.path.exists(destination_path):
        shutil.copy2(source_path, destination_path)
        print(f"{source_path} cloned to {destination_path}")
    else:
        print(f"{destination_path} already exists, use force_overwrite=True to overwrite")
