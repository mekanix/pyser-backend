import os

from config import configs
from pyser import cli, create_app

config_name = os.getenv('FLASK_ENV') or 'default'
app = create_app(configs[config_name])
cli.register(app)

if __name__ == '__main__':
    app.run()
