@app.route('/filemanager/')
@app.route('/filemanager/<path:subpath>')
def file_manager(subpath=None):
    if "logged_in" in session:
        if subpath:
            dir_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
        else:
            dir_path = app.config['UPLOAD_FOLDER']

        if not os.path.exists(dir_path):
            flash('Directory not found.')
            return redirect(url_for('file_manager'))

        items = os.listdir(dir_path)
        files = []
        folders = []

        for item in items:
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                folders.append(item)

        return render_template('file_manager.html', files=files, folders=folders, subpath=subpath)
    else:
        flash("Please log in first")
        return redirect(url_for("login"))

@app.route('/upload/', methods=['POST'])
@app.route('/upload/<path:subpath>', methods=['POST'])
def upload(subpath=None):
    if "logged_in" in session:
        if request.method == 'POST':
            files = request.files.getlist('files')
            if files:
                if subpath:
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
                else:
                    save_path = app.config['UPLOAD_FOLDER']

                for file in files:
                    if isinstance(file, FileStorage):
                        file_path = os.path.join(save_path, secure_filename(file.filename))
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)

                flash('Files uploaded successfully.')
                return redirect(url_for('file_manager', subpath=subpath))
        flash('Error uploading files.')
        return redirect(url_for('file_manager', subpath=subpath))
    else:
        flash("Please log in first")
        return redirect(url_for("login"))

@app.route('/delete/<path:filename>')
def delete(filename):
    if "logged_in" in session:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('File deleted successfully.')
        else:
            flash('File not found.')
        return redirect(url_for('file_manager'))
    else:
        flash("Please log in first")
        return redirect(url_for("login"))

@app.route('/create_folder/', methods=['POST'])
@app.route('/create_folder/<path:subpath>', methods=['POST'])
def create_folder(subpath=None):
    if "logged_in" in session:
        folder_name = request.form['folder_name']
        if subpath:
            parent_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
        else:
            parent_path = app.config['UPLOAD_FOLDER']
        
        new_folder_path = os.path.join(parent_path, folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            flash('Folder created successfully.')
        else:
            flash('Folder already exists.')

        return redirect(url_for('file_manager', subpath=subpath))
    else:
        flash("Please log in first")
        return redirect(url_for("login"))




@app.route('/delete_folder/<path:folder_path>')
def delete_folder(folder_path):
    if "logged_in" in session:
        full_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
        if os.path.exists(full_folder_path):
            shutil.rmtree(full_folder_path)
            flash('Folder deleted successfully.')
        else:
            flash('Folder not found.')

        return redirect(url_for('file_manager'))
    else:
        flash("Please log in first")
        return redirect(url_for("login"))


app.run(host='0.0.0.0', port=5000)
