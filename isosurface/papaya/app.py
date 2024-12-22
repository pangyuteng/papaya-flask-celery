
import os
import sys

from flask import (
    Flask, render_template
)


volume_file = 'example.nii' # not sure why nii.gz can't be loaded!
surface_file_100 = 'example_100.vtk'
surface_file_900 = 'example_900.vtk'

app = Flask(__name__,
    static_url_path='/static',
    static_folder='static',
    template_folder='templates',
)

@app.route('/volume')
def volume():
    return render_template("volume.html",
        volume_file=volume_file
    )

@app.route('/isosurface')
def isosurface():
    return render_template("isosurface.html",
        volume_file=volume_file,
        surface_file_100=surface_file_100,
        surface_file_900=surface_file_900
    )

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port",type=int,default=5000)
    args = parser.parse_args()
    app.run(debug=True,host="0.0.0.0",port=args.port)
