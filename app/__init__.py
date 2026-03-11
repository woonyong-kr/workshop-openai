from flask import Flask, g, session
from werkzeug.middleware.proxy_fix import ProxyFix

from .auth.routes import bp as auth_bp
from .config import Config
from .core.routes import bp as core_bp
from .extensions import get_user_repository, init_extensions
from .mailbox.routes import bp as mailbox_bp


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    if test_config:
        app.config.update(test_config)

    init_extensions(app)
    register_blueprints(app)

    @app.before_request
    def load_current_user():
        g.current_user = None

        user_id = session.get("user_id")
        if not user_id:
            return

        user = get_user_repository().get_by_id(user_id)
        if user is None:
            session.clear()
            return

        g.current_user = user

    @app.context_processor
    def inject_globals():
        hidden_keywords = []
        current_user = g.get("current_user")
        if current_user is not None:
            hidden_keywords = get_user_repository().get_hidden_keywords(current_user)

        return {
            "app_name": app.config["APP_NAME"],
            "app_tagline": app.config["APP_TAGLINE"],
            "current_user": current_user,
            "hidden_keywords": hidden_keywords,
        }

    return app


def register_blueprints(app):
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mailbox_bp)
