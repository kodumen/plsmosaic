from flask import Flask, request, json

app = Flask(__name__)

@app.route('/')
def version():
    return 'pls mosaic 0.0.1a';

@app.route('/', methods=['POST'])
def command():
    if request.form['text'] == '':
        return 'pls mosaic 0.0.1a'

    return json.jsonify({
        'response_type': 'in_channel',
        'text': request.form['text']
        })
