from functools import wraps

import jwt
from flask import request, jsonify


def check_for_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        print(args)
        print(kwargs)
        # if not token:
        #     return jsonify({'message': 'Token missing'}), 403
        #
        # try:
        #     data = jwt.decode(token, app.config['SECRET_KEY'])
        # except:
        #     return jsonify({'message': 'Invalid token'}), 403
        return f(*args, **kwargs)

    return decorated
