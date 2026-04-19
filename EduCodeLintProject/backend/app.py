from flask import Flask

from backend.route.analyze import analyze_bp
from backend.route.compare import compare_bp
from backend.route.record import record_bp
from backend.db.init_database import init_db


def create_app():
    init_db()
    app = Flask(__name__)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(record_bp)
    return app


if __name__ == '__main__':
    app = create_app()
    # 改成这样
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
