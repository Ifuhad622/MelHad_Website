from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../sections')  # Adjust template_folder path as needed

    # Register blueprints
    from .main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
