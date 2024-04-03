import flask,requests,json 
from BTConn import controller

app = flask.Flask(__name__)

@app.route("/")
def home_view():
    return "<p>hello</p>"