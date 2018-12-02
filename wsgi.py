import os

from config import configs
from flask import send_file
from pyser import cli, create_app

config_name = os.getenv('FLASK_ENV') or 'default'
app = create_app(configs[config_name])
cli.register(app)


@app.route('/media/<path:path>')
def send_js(path):
    fullPath = f"{app.config['MEDIA_PATH']}/{path}"
    return send_file(fullPath)


if __name__ == '__main__':
    app.run()
