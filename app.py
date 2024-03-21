import os
from config import create_app

# 创建应用
config_name = os.environ.get('FLASK_ENV')
app = create_app(config_name)
