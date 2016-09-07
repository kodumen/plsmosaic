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
    return 'pls mosaic 0.1.1a';

@app.route('/', methods=['POST'])
def command():
    if request.form['text'] == '':
        return 'pls mosaic 0.1.1a'

    try:
        params = get_params(request.form['text'])
        tmp_file = retrieve_image(params['url'])
        upload_info = cloudinary.uploader.upload(
            tmp_file,
            public_id = params['url_hash']
            )
    except Error as e:
        return str(e)
    
    image_url = get_image_with_mosaic(upload_info, params)

    return json.jsonify({
        'response_type': 'in_channel',
        'text': '*{}*:\n<{}|*Original*>'.format(request.form['user_name'], params['url']),
        'unfurl_links': False,
        'unfurl_media': False,
        'attachments': [
                {
                    'fallback': 'mosaic',
                    'image_url': image_url   
                }
            ]
        })

def get_image_with_mosaic(image, options):
    """
    Apply the mosaic filter to the image.
    options = {
        'scale': scale of the image's width and height,
        'size': 0 to 200, or None for default,
        }
    """
    if options['size'] == None:
        effect = 'pixelate'
    else:
        effect = 'pixelate:{}'.format(options['size'])

    image_url, image_options = cloudinary.utils.cloudinary_url(
        image['public_id'],
        effect = effect,
        width = options['scale'],
        height = options['scale']
        )

    return image_url

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

    [url] [size] [scale]
    """
    tokens = text.split(' ')

    url_info = urlparse(array_value(tokens, 0))
    if url_info.scheme not in ['http', 'https']:
        raise Error('Invalid protocol. Allowed: http, https')

    try:
        scale = float(array_value(tokens, 2))
        scale = min(1.0, max(scale, 0.0))
    except ValueError:
        scale = 1.0

    try:
        size = int(array_value(tokens, 1))
    except ValueError:
        size = None

    return {
        'url': array_value(tokens, 0),
        'url_hash': get_hash(url_info.netloc + url_info.path),
        'scale': scale,
        'size': size
        }

def get_hash(text):
    """
    Return the SHA1 hash of the text.
    """
    hash = hashlib.sha1()
    hash.update(bytes(text, 'utf-8'))
    return hash.hexdigest()

def array_value(array, index, default=''):
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
