from flask import jsonify


def success(data=None, msg="success", code=0):
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data
    })


def error(msg="error", code=1, http_status=400, data=None):
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data
    }), http_status

