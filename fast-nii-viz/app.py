import os
import traceback
import shutil
import tempfile
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import uuid
import flask

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify("hi")

@app.route('/ping')
def ping():
    return jsonify({'status':'pong'})

# transform and create cached files, return json
# return div 
# infinite scroll page to render lots of divs

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)
