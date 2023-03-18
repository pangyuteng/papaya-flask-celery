import os
import traceback
import datetime
import tempfile
import pandas as pd
from flask import (
    Flask, render_template, request, jsonify, url_for, Response
)
from utils import myquery

app = Flask(__name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates',
)

@app.route('/ping')
def ping():
    return jsonify({"status":"pong"})

@app.route('/catalog_csv')
def catalog_csv():
    with tempfile.TemporaryDirectory() as tmpdir:
        
        mylist = myquery()
        df = pd.DataFrame(mylist)
        csv_file = os.path.join(tmpdir,'my.csv')
        df.to_csv(csv_file,index=False)
        with open(csv_file,'r') as f:
            csv_text = f.read()
        tstamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        return Response(
            csv_text,
            mimetype="text/csv",
            headers={"Content-disposition":
                    f"attachment; filename=catalog-{tstamp}.csv"})

@app.route('/')
def home():
    mylist = myquery()
    return render_template('home.html',mylist=mylist)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

