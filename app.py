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
from sqlalchemy import create_engine, func, inspect, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = "Access-Control-Allow-Methods: *"
app.config['DEBUG'] = True
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'verySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/crisis_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["SWAGGER"] = {
#     "specs": [
#         {"version": "1.0", "title": "PROJECT API", "endpoint": "api", "route": "/api"}
#     ]
# }
#
# Swagger(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
db_session = (sessionmaker(bind=engine))
my_session = db_session()
db.init_app(app)
migrate = Migrate(app, db)


def get_right_now():
    return int(round(time.time())) * 1000


@cross_origin()
@app.route('/test/<x>', methods=["GET"])
@check_for_token(app.config['SECRET_KEY'])
def test(x):
    return 'Hello World!' + x


@cross_origin()
@app.route('/add_need', methods=["POST"])
# @check_for_token(app.config['SECRET_KEY'])
def add_need():
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        if "title" in request.json.keys() and "category_id" in request.json.keys():
            need_data = {
                "title": request.json.get("title"),
                "category_id": int(request.json.get("category_id"))
            }
            need = Need(**need_data)
            my_session.add(need)
            my_session.commit()
        else:
            resp = jsonify({'error': "یکی از فیلدها اشتباه است"}), 400
            return resp

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/<token>', methods=["GET"])
def dashboard(token):
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        # get information
        user = my_session.query(User).filter(User.token == token).first()
        if user and get_right_now() < int(user.token_exp):
            resp = jsonify({
                'status': True
            }), 200
        else:
            resp = jsonify({
                'status': False
            }), 200

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/sign-up', methods=["POST"])
def sign_up():
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        # get information
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        phone = request.json.get('phone')
        national_id = request.json.get('national_id')
        address = request.json.get('address')
        allow_location = request.json.get('allow_location')
        lat = request.json.get('lat') if 'lat' in request.json.keys() else ""
        long = request.json.get('long') if 'long' in request.json.keys() else ""
        otp = str(random.randint(1000, 99999))
        otp_exp = str(int(round((time.time() + 300) * 1000))),  # 5 minutes

        # check for duplicates
        dup = my_session.query(User).filter(or_(User.phone == phone, User.national_id == national_id)).first()
        if dup:
            resp = jsonify({'error': "کد ملی یا شماره‌ی تماس قبلاً وارد شده است"}), 401
            return resp

        # create user
        user_data = {
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone,
            "national_id": national_id,
            "address": address,
            "allow_location": allow_location,
            "lat": lat,
            "long": long,
            "otp": otp,
            "otp_exp": otp_exp,
        }
        user = User(**user_data)

        # add user to database
        my_session.add(user)
        my_session.commit()

        # generate response
        resp = jsonify({
            'msg': "ثبت‌نام شما با موفقیت انجام شد، تا لحظاتی دیگر کد تأیید به شماره‌ی تماس شما ارسال می‌شود",
            'otp': {
                'code': otp,
                'exp': otp_exp,
            },
        }), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = make_response(jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500)

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/sign-in', methods=["PATCH"])
def sign_in():
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        # get information
        if 'phone' in request.json.keys():
            login_info = request.json.get('phone')
        elif 'national_id' in request.json.keys():
            login_info = request.json.get('national_id')
        else:
            resp = jsonify({
                'error': "برای ورود باید از بین شماره‌ی تماس و کد ملی یک مورد را وارد نمایید",
            }), 401
            return resp

        # check for existence
        user = my_session.query(User).filter(or_(User.phone == login_info, User.national_id == login_info)).first()
        if not user:
            resp = jsonify({
                'error': "این کد ملی یا شماره‌ی تماس قبلاً ثبت نشده است",
            }), 401
            return resp

        # generating otp
        otp = str(random.randint(1000, 99999))
        otp_exp = str(int(round((time.time() + 300) * 1000))),  # 5 minutes

        # updating user
        user.otp = otp
        user.otp_exp = otp_exp
        my_session.commit()

        # generate response
        resp = jsonify({
            'msg': 'تا لحظاتی دیگر کد تأیید برای شماره‌ی تماس شما ارسال می‌شود',
            'otp': {
                'code': otp,
                'exp': otp_exp
            },
        }), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/verify/<phone>/<otp>', methods=["GET"])
def verify(phone, otp):
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        # get information
        user = my_session.query(User).filter(and_(User.phone == phone, User.otp == otp)).first()
        print(get_right_now())
        print(int(user.otp_exp))
        print(get_right_now() - int(user.otp_exp))
        if not user:
            resp = jsonify({
                'error': "کد وارد شده صحیح نیست",
                'status': 401
            }), 401
            return resp
        elif get_right_now() > int(user.otp_exp):
            resp = jsonify({
                'error': "کد منقضی شده است، مجدداً کد دریافت کنید",
            }), 401
            return resp

        # token payload
        token_exp = int(round((time.time() + 259200) * 1000)),  # 3 days
        payload = {
            "user": {
                "id": user.id,
                "name": f'{user.firstname} {user.lastname}',
                "allow_location": user.allow_location,
            },
            "exp": token_exp[0]
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'])

        # update user
        user.is_verified = True
        user.token = token
        user.token_exp = token_exp

        my_session.commit()

        # generate response
        resp = jsonify({
            'msg': f"{user.fullname} عزیز، با موفقیت وارد شدید",
            'token': 'Bearer ' + token,
        }), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/request/<user_id>', methods=["GET", "POST"])
@check_for_token(app.config['SECRET_KEY'])
def add_request(user_id):
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        if request.method == "POST":
            # get information
            user_id = int(user_id)
            disaster_id = int(request.json.get('type'))
            lat = request.json.get('lat') if 'lat' in request.json.keys() else ""
            long = request.json.get('long') if 'long' in request.json.keys() else ""
            needs = request.json.get('needs')

            for need in needs:
                description = need.get("desc")
                amount = need.get("amount")
                urgent = need.get("urgent")
                need_id = need.get("title")

                # create request
                request_data = {
                    "user_id": user_id,
                    "disaster_id": disaster_id,
                    "lat": lat,
                    "long": long,

                    "description": description,
                    "amount": amount,
                    "urgent": urgent,
                    "need_id": need_id,
                }
                user_request = Request(**request_data)

                # add request to database
                my_session.add(user_request)

            my_session.commit()

            # generate response
            resp = jsonify({
                'msg': "درخواست شما با موفقیت ثبت شد",
            }), 200

        elif request.method == "GET":
            result = []
            requests = my_session.query(Request).filter(Request.user_id == user_id)

            for req in requests:
                result.append({
                    "name": req.need.title,
                    "amount": req.amount,
                    "urgent": req.urgent,
                    "urgent_pretty": req.urgent_pretty,
                    "askDate": req.created_at,
                    "helpDate": req.done_at,
                    "status": req.status,
                    "status_pretty": req.status_pretty,
                    "type": req.disaster.title,
                    "desc": req.description,
                    "info": {
                        "address": req.user.address,
                        "location": {
                            "lat": req.lat,
                            "long": req.long,
                        }
                    },
                })

                # generate response
                resp = jsonify(result), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/get_needs', methods=["GET"])
def get_needs():
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        result = {}
        need_categories = my_session.query(NeedCategory).order_by(NeedCategory.id.asc())

        for category in need_categories:
            needs_temp = {}
            for need in category.needs:
                needs_temp[need.id] = need.title

            result[category.id] = {
                "enName": category.en_title,
                "faName": category.title,
                "items": needs_temp,
            }

        # generate response
        resp = jsonify(result), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


@cross_origin()
@app.route('/profile/<user_id>', methods=["GET", "PUT"])
def profile(user_id):
    resp = jsonify({'error': "خطای سرور"}), 500

    try:
        user_id = int(user_id)
        user = my_session.query(User).filter(User.id == user_id).first()

        if request.method == "GET":
            # generate response
            resp = jsonify({
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
                "national_id": user.national_id,
            }), 200

        elif request.method == "PUT":
            # get information
            if "firstname" in request.json.keys() and request.json["firstname"] is not None:
                user.firstname = request.json["firstname"]
            if "lastname" in request.json.keys() and request.json["lastname"] is not None:
                user.lastname = request.json["lastname"]
            if "email" in request.json.keys() and request.json["email"] is not None:
                user.email = request.json["email"].lower()
            if "address" in request.json.keys() and request.json["address"] is not None:
                user.address = request.json["address"]
            if "phone" in request.json.keys() and request.json["phone"] is not None:
                user.phone = request.json["phone"]
            if "national_id" in request.json.keys() and request.json["national_id"] is not None:
                user.national_id = request.json["national_id"]

            # save changes to database
            my_session.commit()

            # generate response
            resp = jsonify({
                'msg': "تغییرات با موفقیت اعمال شد",
            }), 200

        # close session
        my_session.close()

    except Exception as e:
        print(e)
        resp = jsonify({'error': "مشکلی پیش آمده است، مجدداً تلاش کنید"}), 500

    finally:
        my_session.close()
        return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
