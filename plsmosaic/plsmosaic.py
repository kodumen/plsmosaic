from flask import Flask, request, json
from urllib.parse import urlparse
from urllib.request import urlretrieve
from urllib.error import URLError
import hashlib
import cloudinary.uploader
import cloudinary.utils

app = Flask(__name__)

@app.route('/')
def version():
    return 'pls mosaic 0.0.1a';

@app.route('/', methods=['POST'])
def command():
    if request.form['text'] == '':
        return 'pls mosaic 0.1.0a'

    try:
        params = get_params(request.form['text'])
        tmp_file = retrieve_image(params['url'])
        upload_info = cloudinary.uploader.upload(
            tmp_file,
            public_id = params['url_hash']
            )
    except Error as e:
        return str(e)
    
    # Hard coded numbers because I'm too lazy right now. It's 12:28 AM.
    image_url, image_options = cloudinary.utils.cloudinary_url(
        upload_info['public_id'],
        effect = 'pixelate:{}'.format(upload_info['width'] // 50 * 3 // 4),
        width = upload_info['width'] * 3 // 4,
        height = upload_info['height'] * 3 // 4
        )

    return json.jsonify({
        'response_type': 'in_channel',
        'text': '*{}*:\n<{}|*Original*>'.format(request.form['user_name'], request.form['text']),
        'unfurl_links': False,
        'unfurl_media': False,
        'attachments': [
                {
                    'fallback': 'mosaic',
                    'image_url': image_url   
                }
            ]
        })

def retrieve_image(url):
    """
    Try to retrieve the image from the url.
    Returns the temporary file where the image is stored.
    """
    try:
        tmp_file, image_info = urlretrieve(url)
    except URLError:
        raise Error('Unable to get file.')

    if not image_info.get_content_type().startswith('image/'):
        raise Error('Invalid content type. Allowed: image/*')

    return tmp_file

def get_params(text):
    """
    Return a dictionary of the parameters and their values.
    Raise an error if url is invalid.
    """
    tokens = text.split(' ')
    url_info = urlparse(array_value(tokens, 0, ''))

    if url_info.scheme not in ['http', 'https']:
        raise Error('Invalid protocol. Allowed: http, https')

    return {
        'url': array_value(tokens, 0, ''),
        'url_hash': get_hash(url_info.netloc + url_info.path)
        }

def get_hash(text):
    """
    Return the SHA1 hash of the text.
    """
    hash = hashlib.sha1()
    hash.update(bytes(text, 'utf-8'))
    return hash.hexdigest()

def array_value(array, index, default=None):
    """
    Get the value in the array's index or a default value.
    """
    try:
        return array[index]
    except IndexError:
        return default


class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    pass
