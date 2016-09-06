from flask import Flask, request, json
from urllib.parse import urlparse
from urllib.request import urlretrieve
import cloudinary.uploader

app = Flask(__name__)

@app.route('/')
def version():
    return 'pls mosaic 0.0.1a';

@app.route('/', methods=['POST'])
def command():
    if request.form['text'] == '':
        return 'pls mosaic 0.0.1a'

    url_info = urlparse(request.form['text'])
    if url_info.scheme not in ('http', 'https'):
        return 'Invalid protocol. Allowed: HTTP, HTTPS.'

    tmp_file, image_info = urlretrieve(request.form['text'])
    if not image_info.get_content_type().startswith('image/'):
        return 'Invalid content type. Allowed: image/*'

    upload_info = cloudinary.uploader.upload(tmp_file)

    return json.jsonify({
        'response_type': 'in_channel',
        'text': upload_info['secure_url']
        })
