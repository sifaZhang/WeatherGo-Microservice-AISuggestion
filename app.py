import flask
app = flask.Flask(__name__)
@app.route('/')
def index():
    return 'API Works!'

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')