from plotly.offline import plot
from plotly.graph_objs import Scatter
from flask import Flask, render_template, request, jsonify


app = Flask(__name__,
    static_url_path='', 
    static_folder='static',
    template_folder='templates',
)

@app.route("/ping")
def ping():
    return jsonify(success=True)

@app.route('/')
def home():
    x_data = [0,1,2,3]
    y_data = [x**2 for x in x_data]
    plot_div = plot([
        Scatter(x=x_data, y=y_data,
            mode='lines', name='test',
            opacity=0.8, marker_color='green')
        ],output_type='div',include_plotlyjs=False)
    return render_template("index.html", plot_div=plot_div)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")


"""

ref. https://www.reddit.com/r/flask/comments/o9nvf5/comment/h3du6q7/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

python3.8 -m venv /mnt/scratch/venv/finance
source /mnt/scratch/venv/finance/bin/activate
pip install -r requirements.txt


"""