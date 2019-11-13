from config import configs
from pyser import create_app

config = configs['development']
app = create_app(config)
