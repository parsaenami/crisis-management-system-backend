import os
import random

import jwt

from auth import check_for_token
from models import *
from flask import Flask, request, jsonify, make_response
from flask_script import Manager
from flask_bcrypt import Bcrypt
from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flasgger import Swagger, swag_from
from sqlalchemy import create_engine, func, inspect, or_
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Access-Control-Allow-Methods: *"
app.config['DEBUG'] = True
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'verySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/crisis_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SWAGGER"] = {
    "specs": [
        {"version": "1.0", "title": "PROJECT API", "endpoint": "api", "route": "/api"}
    ]
}

Swagger(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
db_session = (sessionmaker(bind=engine))
my_session = db_session()
db.init_app(app)
migrate = Migrate(app, db)


@cross_origin()
@app.route('/<x>', methods=["GET"])
def hello_world(x):
    return 'Hello World!'


@cross_origin()
@app.route('/dashboard', methods=["GET"])
def get_otp():
    return 'Hello World 1!'


@cross_origin()
@app.route('/sign-up', methods=["POST"])
def sign_up():
    resp = make_response(jsonify({'error': "خطای سرور", 'status': 500}), 500)

    try:
        # get information
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        phone = request.json.get('phone')
        national_id = request.json.get('national_id')
        address = request.json.get('address')
        allow_location = request.json.get('allow_location')
        otp = str(random.randint(1000, 99999))

        # check for duplicates
        dup = my_session.query(User).filter(or_(User.phone == phone, User.national_id == national_id)).first()
        if dup:
            resp = make_response(jsonify({'error': "کد ملی یا شماره‌ی تماس قبلاً وارد شده است", 'status': 401}), 401)
            return resp

        # token payload
        payload = {
            "user": {
                "name": f'{firstname} {lastname}',
                "allow_location": allow_location,
            },
            "exp": int(round((time.time() + 259200000) * 1000)),  # 3 days
        }

        token = jwt.encode(payload, app.config['SECRET_KEY'])

        # create user
        user_data = {
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone,
            "national_id": national_id,
            "address": address,
            "allow_location": allow_location,
            "otp": otp,
            "token": token,
        }
        user = User(**user_data)

        # add user to database
        my_session.add(user)
        my_session.commit()

        # generating response
        resp = (jsonify({
            'msg': "ثبت‌نام شما با موفقیت انجام شد",
            'otp': {
                'code': otp,
                'exp': int(round((time.time() + 300000) * 1000)),  # 5 minutes
            },
            'token': 'Bearer ' + token,
            'status': 200,
        }), 200)

        # closing session
        my_session.close()

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "something is wrong!", 'status': 500}), 500)

    finally:
        my_session.close()
        return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
