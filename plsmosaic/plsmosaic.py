from flask import Flask, request, json
from urllib.parse import urlparse
from urllib.request import urlretrieve
import cloudinary.uploader
import cloudinary.utils

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
    
    # Hard coded numbers because I'm too lazy right now. It's 12:28 AM.
    image_url, image_options = cloudinary.utils.cloudinary_url(
        upload_info['public_id'],
        effect = 'pixelate:{}'.format(50 * 3 // 4),
        width = upload_info['width'] * 3 // 4,
        height = upload_info['height'] * 3 // 4
        )

    return json.jsonify({
        'response_type': 'in_channel',
        'text': '*{}*:\n<{}|*Original*>'.format(request.form['user_name'], request.form['text']),
        'unfurl_links': false,
        'unfurl_media': false,
        'attachments': [
            'fallback': 'mosaic',
            'image_url': image_url
            ]
        })
