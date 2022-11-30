import os
import main
import urllib.request

from re import sub
from requests import get
from main import getPrediction
from socket import gethostname
from werkzeug.utils import secure_filename
from flask import Flask, render_template, make_response, request, redirect, flash, url_for

UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
app.secret_key = 'inf-0047'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder is not exists
if not os.path.isdir(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def submit_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            getPrediction(filename)
            label, acc = getPrediction(filename)
            flash(label)
            flash(acc)
            flash(filename)
            return redirect('/')


@app.route('/status')
def health():
    template = render_template('status.html', hostname=gethostname(), zone=_get_zone())
    return make_response(template, 200)


def _get_zone():
    """Gets the GCE zone of this instance.
    Returns:
        str: The name of the zone if the zone was successfully determined.
        Empty string otherwise.
    """
    r = get('http://metadata.google.internal/'
            'computeMetadata/v1/instance/zone',
            headers={'Metadata-Flavor': 'Google'})
    if r.status_code == 200:
        return sub(r'.+zones/(.+)', r'\1', r.text)
    else:
        return ''


if __name__ == "__main__":
    app.run(debug=False, port=80)
