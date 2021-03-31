from flask import Flask, render_template, redirect, url_for, request, flash, make_response, Markup
from werkzeug.utils import secure_filename
import sys
import io
import os
from pathlib import Path
import json
# import requests
# import time

from PIL import Image

import renderer
import junkdrawer

buffer = io.StringIO()

app = Flask(__name__)
app.secret_key = 'Fractals'
# APP_ROOT = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join('/static', 'Saved_Animations')


@app.route('/')
def home():
    liLinkNames = ['Home',
                   'Make a Fractal',
                   'Clone a Fractal',
                   'Debug Print']
    liLinks = [url_for('home'),
               url_for('gif_page', filename='Plant_2020-09-13_20-27-07.gif'),
               url_for('cloner'),
               url_for('printing')]
    return render_template('main.html',
                           title="Home",
                           linkCount=len(liLinkNames),
                           linkNames=liLinkNames,
                           Links=liLinks,
                           salutation="Welcome to the Lindenmayer Fractals Web App!",
                           image1='/static/Example_Fractal.gif')


@app.route('/static/gif/<filename>')
def gif_page(filename):
    liLinkNames = ['Home', 'Make a Fractal']
    liLinks = [url_for('home'), url_for('gif_page', filename='Plant_2020-09-13_20-27-07.gif')]
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('main.html',
                           title="Gif: " + filename,
                           linkCount=len(liLinkNames),
                           linkNames=liLinkNames,
                           Links=liLinks,
                           image1=full_filename)


@app.route('/clone', methods=['POST', 'GET'])
def cloner():
    global buffer
    # chosenFile = "Didn't work"
    # chosenFile = request.args.get('file', '')
    # if a file is specified, post to that file and start cloning
    if request.method == 'POST':
        if 'myfile' not in request.files:
            flash("No myfile in POST")
            return redirect(request.url)
        chosenFile = request.files['myfile']
        if chosenFile.filename == '':
            flash("No selected file")
            return redirect(request.url)
        filename = secure_filename(chosenFile.filename)
        if chosenFile and filename.rsplit('.', 1)[1].lower() == "gif":
            fileFullName = os.path.join(Path(__file__).parent, 'static', 'Saved_Animations', filename)
            chosenFile.save(fileFullName)
            with Image.open(fileFullName) as imgGif:
                jsonBlueprint = imgGif.info["comment"].decode('ASCII')
            with open(os.path.join(Path(__file__).parent, 'static', 'blueprint.json'), 'w+') as f:
                f.truncate(0)
                f.seek(0)
                f.write(jsonBlueprint)
            return redirect(url_for('making'))
        else:
            flash("Unexpected File Type")
            return redirect(request.url)
    else:
        return render_template('fileupload.html')


@app.route('/making', methods=['GET'])
def making():
    return render_template('making.html', blueprintPath="blueprint.json")


@app.route('/maker_script', methods=['POST'])
def make_a_gif():
    with open(os.path.join(Path(__file__).parent, 'static', request.form['blueprint']), 'r') as f:
        jsonBlueprint = f.read()
    dctMakerKey = json.loads(jsonBlueprint, cls=junkdrawer.JeffSONDecoder)
    sResponse = renderer.render_2d_frame_by_frame_animation(**dctMakerKey)
    sResponse = sResponse.rsplit('/', 1)[1]
    return make_response(sResponse, 200)


@app.route('/test_printing')
def printing():
    for i in range(10):
        print("test")
    liLinkNames = ['Home',
                   'Make a Fractal',
                   'Clone a Fractal',
                   'Debug Print']
    liLinks = [url_for('home'),
               url_for('gif_page', filename='Plant_2020-09-13_20-27-07.gif'),
               url_for('cloner'),
               url_for('printing')]
    return render_template('main.html',
                           title="Debugging",
                           linkCount=len(liLinkNames),
                           linkNames=liLinkNames,
                           Links=liLinks,
                           body2=get_console())


@app.route('/get_console', methods=['GET'])
def get_console():
    global buffer
    lines = request.args.get('lines')
    escape = request.args.get('escape')
    strOut = buffer.getvalue()
    if lines:
        try:
            lines = int(lines)
            liOut = strOut.splitlines()
            if len(liOut) < lines:
                liOut += [''] * (lines - len(liOut))
            strOut = "\n".join(liOut[-lines:])
        except Exception as e:
            return "unknown lines parameter passed"
    if escape:
        strOut = str(Markup.escape(strOut))
        strOut = strOut.replace("\n", "<br>")
    return strOut


@app.route('/reset_logs', methods=['GET'])
def reset_logs():
    buffer.truncate(0)
    buffer.seek(0)
    return redirect(url_for('home'))


def main():
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        app.run(debug=True)
    finally:
        sys.stdout = old_stdout


if __name__ == "__main__":
    main()
