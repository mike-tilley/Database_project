import json
from flask import Flask, request, Response



# creating web framework functionality
app = Flask(__name__)


# routes go here
@app.route("/")
def index():
    return Response(json.dumps("home page"), status=200, mimetype="application/json")

@app.route("/ping")
def ping():
    return Response(json.dumps("PONG"), status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)
