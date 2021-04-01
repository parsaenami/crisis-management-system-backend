import time
from datetime import datetime
import sqlalchemy as sa

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import scoped_session, object_session, backref

db = SQLAlchemy()

request_statuses = {
    0: "در انتظار تأیید",
    1: "تأیید شده",
    2: "رد شده",
    3: "در حال ارسال",
    4: "در حال آماده‌سازی",
    5: "ارسال شده",
    6: "دریافت شده",
}
urgent_mappings = {
    1: "خیلی کم",
    2: "کم",
    3: "متوسط",
    4: "زیاد",
    5: "خیلی زیاد",
}


def obj_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


class User(db.Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    firstname = sa.Column(sa.String, nullable=False)
    lastname = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=True, default=None)
    address = sa.Column(sa.String, nullable=False)
    phone = sa.Column(sa.String, nullable=False)
    national_id = sa.Column(sa.String, nullable=False)
    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)
    allow_location = sa.Column(sa.Boolean, nullable=False, default=False)
    lat = sa.Column(sa.String, nullable=True, default="")
    long = sa.Column(sa.String, nullable=True, default="")
    otp = sa.Column(sa.String, nullable=False, default="")
    otp_exp = sa.Column(sa.String, nullable=True, default="")
    token = sa.Column(sa.String, nullable=False, default="")
    token_exp = sa.Column(sa.String, nullable=True, default="")
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))

    requests = sa.orm.relationship(
        "Request",
        back_populates="user",
    )

    @hybrid_property
    def location(self):
        return {
            "allow": self.allow_location,
            "lat": self.lat,
            "long": self.long,
        }

    @hybrid_property
    def fullname(self):
        return f'{self.firstname} {self.lastname}'


class NeedCategory(db.Model):
    __tablename__ = "need_category"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    en_title = sa.Column(sa.String, nullable=True)

    needs = sa.orm.relationship(
        "Need",
        back_populates="category",
    )


class Need(db.Model):
    __tablename__ = "need"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))

    category_id = sa.Column(sa.Integer, sa.ForeignKey("need_category.id"), nullable=False)

    category = sa.orm.relationship(
        "NeedCategory",
        uselist=False,
        back_populates="needs",
    )
    requests = sa.orm.relationship(
        "Request",
        back_populates="need",
    )


class DisasterCategory(db.Model):
    __tablename__ = "disaster_category"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    en_title = sa.Column(sa.String, nullable=True)

    requests = sa.orm.relationship(
        "Request",
        back_populates="disaster",
    )


class Request(db.Model):
    __tablename__ = "request"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    description = sa.Column(sa.String, nullable=True)
    amount = sa.Column(sa.Integer, nullable=False)
    urgent = sa.Column(sa.Integer, nullable=False, default=3)
    status = sa.Column(sa.Integer, nullable=False, default=0)
    lat = sa.Column(sa.String, nullable=True, default="")
    long = sa.Column(sa.String, nullable=True, default="")
    created_at = sa.Column(sa.String, nullable=False, default=str(int(round(time.time() * 1000))))
    done_at = sa.Column(sa.String, nullable=True)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    need_id = sa.Column(sa.Integer, sa.ForeignKey("need.id"), nullable=False)
    disaster_id = sa.Column(sa.Integer, sa.ForeignKey("disaster_category.id"), nullable=False)

    user = sa.orm.relationship(
        "User",
        uselist=False,
        back_populates="requests",
    )
    need = sa.orm.relationship(
        "Need",
        uselist=False,
        back_populates="requests",
    )
    disaster = sa.orm.relationship(
        "DisasterCategory",
        uselist=False,
        back_populates="requests",
    )

    @hybrid_property
    def status_pretty(self):
        if self.status not in request_statuses.keys():
            return 'نامشخص'
        else:
            return request_statuses[self.status]

    @hybrid_property
    def urgent_pretty(self):
        return urgent_mappings[self.urgent]

    @hybrid_property
    def location(self):
        return {
            "lat": self.lat,
            "long": self.long,
        }
