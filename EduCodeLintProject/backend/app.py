from flask import Flask

from routes.analyze import upload_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(upload_bp)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
