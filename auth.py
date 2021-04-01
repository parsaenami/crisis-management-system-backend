import time
from functools import wraps

import jwt
from flask import request, jsonify


def check_for_token(jwt_key):
    def api_func(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authentication')

            if token:
                decoded_token = jwt.decode(token, jwt_key, "HS256")
                if (decoded_token.get("exp") - (round(time.time())) * 1000 > 0
                        and int(decoded_token.get("user").get("id")) == int(kwargs.get("user_id"))):
                    return func(*args, **kwargs)
                else:
                    return jsonify({"msg": "not allowed"}), 401
            else:
                return jsonify({"msg": "not allowed"}), 401

        return decorated

    return api_func
