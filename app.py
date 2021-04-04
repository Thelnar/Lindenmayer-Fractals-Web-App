from flask import Flask, render_template, redirect, url_for, request, flash, make_response, Markup
from werkzeug.utils import secure_filename
import sys
import io
import os
from pathlib import Path
import json
import random
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
    """
    Home page for the app.
    """
    dctLinks = {
        'Home': url_for('home'),
        'View All Gifs': url_for('gallery'),
        'Clone From Gif': url_for('submit_gif', askfor='clone'),
        'Grab Json From Gif': url_for('submit_gif', askfor='json'),
        'Make From Json': url_for('update_blueprint_json', goto='making'),
        'View Random Gif': url_for('random_gif'),
        'View Console Logs': url_for('printing')

    }
    return render_template('main.html',
                           title="Home",
                           dctLinks=dctLinks,
                           salutation="Welcome to the Lindenmayer Fractals Web App!",
                           images=['/static/Example_Fractal.gif'])


@app.route('/static/gif/<filename>')
def gif_page(filename):
    """
    Interactive page for viewing a fractal in Saved_Animations
    """
    dctLinks = {
        'Home': url_for('home'),
        'View Json': url_for('json_page', filename=filename),
        'Generate Gif': url_for('making'),
        'View Random Gif': url_for('random_gif'),
    }
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('main.html',
                           title="Gif: " + filename,
                           dctLinks=dctLinks,
                           images=[full_filename])


@app.route('/static/json/<filename>')
def json_page(filename):
    """
    Retrieve makerkey json file from comment of a given fractal in Saved_Animations
    """
    if filename.rsplit('.', 1)[1].lower() != "gif":
        flash('File Chosen Not Gif')
        return redirect(url_for('Home'))
    sFileFullName = os.path.join(Path(__file__).parent, 'static', 'Saved_Animations', filename)
    with Image.open(sFileFullName) as imgGif:
        jsonBlueprint = imgGif.info["comment"].decode('ASCII')
    return Markup.escape(jsonBlueprint)


@app.route('/gallery')
def gallery():
    """
    Display all fractals stored in Saved_Animations.
    """
    dctLinks = {
        'Home': url_for('home'),
    }
    liImages = os.listdir(os.path.join('static', 'Saved_Animations'))
    liImages = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in liImages]
    return render_template('main.html',
                           title="Gallery",
                           dctLinks=dctLinks,
                           images=liImages
                           )


@app.route('/random')
def random_gif():
    """
    Redirect to a random gif_page.
    """
    fRandomGif = random.choice(os.listdir(os.path.join(Path(__file__).parent, 'static', 'Saved_Animations')))
    return redirect(url_for('gif_page', filename=fRandomGif))


@app.route('/submit_gif', methods=['POST', 'GET'])
def submit_gif():
    """
    Save gif supplied to Saved_Animations.
    Can return json data or use that json data to create new fractal.
    """
    # if a file is specified, post to that file and start cloning
    sAskFor = request.args.get('askfor')
    if request.method == 'POST':
        if 'myfile' not in request.files:
            flash("No myfile in POST")
            return redirect(request.url)
        fileChosen = request.files['myfile']
        if fileChosen.filename == '':
            flash("No selected file")
            return redirect(request.url)
        sFileName = secure_filename(fileChosen.filename)
        if fileChosen and sFileName.rsplit('.', 1)[1].lower() == "gif":
            sFileFullName = os.path.join(Path(__file__).parent, 'static', 'Saved_Animations', sFileName)
            fileChosen.save(sFileFullName)
            if sAskFor == 'nothing':
                flash(sFileName + " uploaded")
                return redirect(url_for('home'))
            with Image.open(sFileFullName) as imgGif:
                jsonBlueprint = imgGif.info["comment"].decode('ASCII')
            if sAskFor == 'json':
                return Markup.escape(jsonBlueprint)
            # Default behavior is to clone the gif
            with open(os.path.join(Path(__file__).parent, 'static', 'blueprint.json'), 'w+') as f:
                f.truncate(0)
                f.seek(0)
                f.write(jsonBlueprint)
            return redirect(url_for('making'))
        else:
            flash("Unexpected File Type")
            return redirect(request.url)
    else:
        return render_template('fileupload.html', postto=request.url)


@app.route('/update_blueprint', methods=['POST', 'GET'])
def update_blueprint_json():
    """
    Update the blueprint.json used to supply the maker function.
    """
    if request.method == 'POST':
        if 'myfile' not in request.files:
            flash("No myfile in POST")
            return redirect(request.url)
        fileChosen = request.files['myfile']
        if fileChosen.filename == '':
            flash("No selected file")
            return redirect(request.url)
        sFileName = secure_filename(fileChosen.filename)
        if not(fileChosen and sFileName.rsplit('.', 1)[1].lower() in ["json", "txt"]):
            flash("Invalid file submitted")
            flash((sFileName.rsplit('.', 1)[1].lower()))
        else:
            sFileFullName = os.path.join(Path(__file__).parent, 'static', 'blueprint.json')
            fileChosen.save(sFileFullName)
            flash(sFileName + " set to blueprint")
            if request.args.get('goto'):
                return redirect(url_for(request.args.get('goto')))
        return redirect(url_for('home'))
    else:
        return render_template('fileupload.html', postto=request.url)


@app.route('/making', methods=['GET'])
def making():
    """
    Generate a new fractal based on the blueprint.json.
    loading.html contains javascript to show console logs while fractal generates. Redirects when finished.
    """
    return render_template('loading.html',
                           ajaxType='POST',
                           ajaxUrl=request.url_root + url_for('make_a_gif')[1:],
                           ajaxData="{ 'blueprint' : 'blueprint.json' }",
                           ajaxSuccess="window.location.replace('" +
                                       url_for('gif_page', filename='') +
                                       "' + response);"
                           )


@app.route('/maker_script', methods=['POST'])
def make_a_gif():
    """
    Script to generate a fractal based on the supplied .json filename.
    """
    with open(os.path.join(Path(__file__).parent, 'static', request.form['blueprint']), 'r') as f:
        jsonBlueprint = f.read()
    dctMakerKey = json.loads(jsonBlueprint, cls=junkdrawer.JeffSONDecoder)
    sResponse = renderer.render_2d_frame_by_frame_animation(**dctMakerKey)
    sResponse = sResponse.rsplit('/', 1)[1]
    return make_response(sResponse, 200)


@app.route('/test_printing')
def printing():
    """
    View console logs for debugging purposes.
    """
    dctLinks = {
        'Home': url_for('home'),
    }
    return render_template('main.html',
                           title="Debugging",
                           dctLinks=dctLinks,
                           body2=get_console())


@app.route('/get_console', methods=['GET'])
def get_console():
    """
    Return html-friendly console logs.
    Query string params:
    escape: any value will prep logs for html insertion
    lines: returns the last x lines
    """
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
    """
    Reset the console logs and redirect to home.
    """
    buffer.truncate(0)
    buffer.seek(0)
    flash("Logs Reset")
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
