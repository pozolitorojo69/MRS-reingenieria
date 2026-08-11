from flask import Flask

from config.config import get_config
from app.utils.database import close_db


def create_app(config_class=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class or get_config())

    from app.blueprints.main.routes import bp as main_bp
    from app.blueprints.api.routes import bp as api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    app.teardown_appcontext(close_db)

    return app