from flask import Flask
from fkask import request
from werkzeug.utils import sercure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello_wourld():
    return 'Hello, world!'

@app.route('/upload, methods=['POST'])
def upload_file():
    f = request.files('the_file')
    f.save('' + secure_filename(f.filename)) # TODO: where to put it?
