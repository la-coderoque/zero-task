import os
import uuid

from flask import Flask, redirect, request
from flask_httpauth import HTTPBasicAuth

from config import ADMIN_LOGIN, ADMIN_PASSWORD, UPLOAD_FOLDER
from db import get_files, save_file


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def authenticate(login, password):
    if login and password:
        if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            return True
        else:
            return False
    return False


@app.route('/', methods=['GET'])
@auth.login_required
def main_page():
    statistics = ''
    if files := get_files():
        statistics += f'Total number of objects: {len(files)}\n'
        labeled_files = [file for file in files if file[1]]
        statistics += f'Number of labeled: {len(labeled_files)}\n'
        if labeled_files:
            statistics += 'Classes (classifications)\n'
        classes = {}
        for file in labeled_files:
            class_ = file[1]
            if class_ not in classes:
                classes[class_] = 1
            else:
                classes[class_] += 1
        for class_ in classes:
            statistics += f'- {class_}: {classes[class_]}\n'

    return f'''
    <!DOCTYPE html>
    <html lang="en">

    <head>
      <meta charset="UTF-8">
      <title>admin</title>
    </head>

    <body>
      <form method="POST" enctype="multipart/form-data">
        <h2>Select images</h2>
        <input type="file" name="files" multiple="true">
        <h2>Classes for dataset</h2>
        <input type="text" name="text">
        <h2>Launch</h2>
        <input type="submit" value="Submit">
      </form>
      <h2>Statistics</h2>
      <pre>{statistics}</pre>
    </body>
    </html>
    '''


@app.route('/', methods=['POST'])
@auth.login_required
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if len(files) == 1 and files[0].headers['Content-Type'] == 'application/octet-stream':
            return '<h2>No attached files!</h2>'
        classes = request.form['text']
        if len(set(classes.split(', '))) < 2:
            return '<h2>Invalid classes string!</h2>'
        for file in files:
            if file and allowed_file(file.filename):
                filename = str(uuid.uuid4())
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                save_file(filename=filename, classes=classes)
    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
