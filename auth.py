from functools import wraps

import jwt
from flask import request, jsonify


def check_for_token(func):
    @wraps(func)
    def decorated(*args):
        # token = request.headers.get('Authentication')
        token = request.headers.get('fuck')

        if token:
            return func(*args, foo=token)
        else:
            return jsonify({"msg": "not allowed"})

    return decorated
