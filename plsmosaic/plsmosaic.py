from flask import Flask

app = Flask(__name__)

@app.route('/')
def app():
    return 'pls mosaic 0.0.1a';
