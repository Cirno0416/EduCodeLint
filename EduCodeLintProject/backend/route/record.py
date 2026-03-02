from flask import Blueprint

record_bp = Blueprint('record', __name__)


@record_bp.route('/records', methods=['GET'])
def get_records():
    pass
