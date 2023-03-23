import shutil

def clone_file(/home/ec2-user/bot/log.txt, /var/www/html/data/, force_overwrite=False):
    try:
        if force_overwrite:
            shutil.copy2(source_path, destination_path)
        else:
            shutil.copy2(source_path, destination_path + '/' + os.path.basename(source_path))
        print("File cloned successfully!")
    except Exception as e:
        print(f"Error: {e}")
        
        
        
        
        

