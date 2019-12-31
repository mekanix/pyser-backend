import os
import socket

from config import configs
from freenit import create_app
from name import app_name
from pyser.api import create_api

config_name = os.getenv('FLASK_ENV') or 'default'
config = configs[config_name]
auth = {
    'user': f'{app_name}.models.user',
    'role': f'{app_name}.models.role',
}
schemas = {
    'user': f'{app_name}.schemas.user',
}
app = create_app(config, app_name, auth=auth, schemas=schemas)
create_api(app)
hostname = socket.gethostname()
port = os.environ.get('FLASK_PORT', 5000)
REDOC_PATH = f'{config.OPENAPI_URL_PREFIX}{config.OPENAPI_REDOC_PATH}'
REDOC_URL = f'http://{hostname}:{port}{REDOC_PATH}'
SWAGGER_PATH = f'{config.OPENAPI_URL_PREFIX}{config.OPENAPI_SWAGGER_UI_PATH}'
SWAGGER_URL = f'http://{hostname}:{port}{SWAGGER_PATH}'

if __name__ == '__main__':
    print(' * ReDoc URL:', REDOC_URL)
    print(' * Swagger URL:', SWAGGER_URL)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True,
    )
