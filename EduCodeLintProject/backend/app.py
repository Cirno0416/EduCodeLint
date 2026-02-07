from flask import Flask

from route.analyze import analyze_bp
from route.compare import compare_bp
from backend.db.init_database import init_db


def create_app():
    # 如果数据库不存在则初始化
    init_db()

    # 创建Flask应用并注册蓝图
    app = Flask(__name__)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(compare_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
