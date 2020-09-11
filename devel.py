from config import configs
from freenit import create_app

config = configs['development']
app = create_app(config)
