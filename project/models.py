from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DB_URL = "sqlite:///crm.db"

my_apply = Flask("ITEA_PROJECT")
my_apply.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(my_apply)

class Dictionary_type(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('dictionary_type.id', ondelete='SET NULL'), nullable=False)

class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    dep_name = db.Column(db.String(100), nullable=False)
    dt_upd = db.Column(db.DateTime, nullable=False)

class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    position = db.Column(db.Integer, db.ForeignKey('dictionary.id', ondelete='SET NULL'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    dt_update = db.Column(db.DateTime, nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)

class Telegram_logs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(100), nullable=False)

class Telegram_users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('dictionary.id', ondelete='SET NULL'), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    is_subsribed = db.Column(db.Integer, nullable=False)

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    dt_upd = db.Column(db.DateTime, nullable=False)

class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_connect = db.Column(db.String(100), nullable=False)
    dt_add = db.Column(db.DateTime, nullable=False)
    dt_session_logout = db.Column(db.DateTime, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)