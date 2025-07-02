import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.root_path, '..', 'received_files'), exist_ok=True)
    except OSError as e:
        app.logger.error(f"Error creating directories: {e}")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app