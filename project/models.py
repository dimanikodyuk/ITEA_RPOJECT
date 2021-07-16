from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    is_subsсribed = db.Column(db.Integer, nullable=False)


# class Customers(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     dt_add = db.Column(db.DateTime, nullable=False)
#     full_name = db.Column(db.String(100), nullable=False)
#     login = db.Column(db.String(100), nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     dt_upd = db.Column(db.DateTime, nullable=False)


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_connect = db.Column(db.String(100), nullable=False)
    dt_add = db.Column(db.DateTime, nullable=False)
    dt_session_logout = db.Column(db.DateTime, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('telegram_users.id', ondelete='SET NULL'), nullable=False)
    executor_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=False)
    dt_upd = db.Column(db.DateTime, nullable=False)


def create_log(p_source, p_comment):
    dt = datetime.now()
    log = Log(dt_add=dt, source=p_source, comment=p_comment)
    db.session.add(log)
    db.session.commit()


# Проверка наличия департамента в БД по названию
def check_dep_name(p_dep_name):
    # запрос в БД
    sql_dep = db.select(Departments.id).where(Departments.dep_name == f'{p_dep_name}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res


# Проверка наличия департамента в БД по id
def check_dep_id(p_dep_id):
    # запрос в БД
    sql_dep = db.select(Departments.id).where(Departments.id == f'{p_dep_id}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res


# Получить список всех департаментов, входной параметр - к-во записей
def get_dep_list(p_count_row=0):
    res_arr = []
    if p_count_row == 0:
        dep_all = db.session.query(Departments).all()
    else:
        dep_all = db.session.query(Departments).limit(p_count_row).all()
    for i in dep_all:
        res_arr.append((i.__dict__['id'], i.__dict__['dep_name']))
    return res_arr


# Проверка наличия сотрудника в БД по ФИО
def check_emp(p_fio):
    # запрос в БД
    sql_dep = db.select(Employees.id).where(Employees.full_name == f'{p_fio}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res


# Проверка наличия сотрудника в БД по id
def check_emp_id(p_emp_id):
    # запрос в БД
    sql_dep = db.select(Employees.id).where(Employees.id == f'{p_emp_id}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res


# Получить список всех сотрудников, входной параметр - к-во записей
def get_emp_list(p_count_row=0):
    res_arr = []
    if p_count_row == 0:
        emp_all = db.session.query(Employees).all()
    else:
        emp_all = db.session.query(Employees).limit(p_count_row).all()
    for i in emp_all:
        res_arr.append((i.__dict__['id'], i.__dict__['full_name'], i.__dict__['position'], i.__dict__['department_id']))
    return res_arr


# Вывод значений словаря по type_id
def get_dictionary_value_list(p_dict_type_id):
    res_arr = []
    dict = db.session.query(Dictionary.id, Dictionary.description).filter(Dictionary.type_id == p_dict_type_id).all()
    for i in dict:
        res_arr.append((i['id'], i['description']))
    return res_arr


# Получить список всех заявок, входной параметр - к-во записей
def get_app_list(p_count_row=0):
    res_arr = []
    if p_count_row == 0:
        app_all = db.session.query(Application).all()
    else:
        app_all = db.session.query(Application).limit(p_count_row).all()
    for i in app_all:
        res_arr.append((i.__dict__['id'], i.__dict__['dt_add'], i.__dict__['type'], i.__dict__['description'],
                        i.__dict__['status'], i.__dict__['code'], i.__dict__['creator_id'], i.__dict__['executor_id'],
                        i.__dict__['dt_upd']))
    return res_arr
