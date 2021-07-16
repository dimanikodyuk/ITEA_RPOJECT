from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

DB_URL = "sqlite:///project/crm.db"

my_apply = Flask("ITEA_PROJECT")
my_apply.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
my_apply.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    dt_upd = db.Column(db.DateTime, nullable=False)


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
    is_subscribed = db.Column(db.Integer, nullable=False)


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
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=False)


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


# Очистка всех сессий (таблица crm.sessions)
db.session.query(Sessions).delete()
db.session.commit()


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
    if p_count_row == "0":
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
        emp_all = db.session.query(Employees, Dictionary).outerjoin(Dictionary).where(
            db.and_(Employees.position == Dictionary.id, Dictionary.type_id == 1)).all()

    else:
        emp_all = db.session.query(Employees, Dictionary).outerjoin(Dictionary).where(
            db.and_(Employees.position == Dictionary.id, Dictionary.type_id == 1)).limit(p_count_row).all()

    for emp, diction in emp_all:
        res_arr.append((emp.id, emp.full_name, diction.description, 0))

    return res_arr

    # res_arr = []
    # if p_count_row == 0:
    #     emp_all = db.session.query(Employees).all()
    # else:
    #     emp_all = db.session.query(Employees).limit(p_count_row).all()
    # for i in emp_all:
    #     res_arr.append((i.__dict__['id'], i.__dict__['full_name'], i.__dict__['position'], i.__dict__['department_id']))
    # return res_arr






# Вывод значений словаря по type_id
def get_dictionary_value_list(p_dict_type_id):
    res_arr = []
    diction = db.session.query(Dictionary.id, Dictionary.description).filter(Dictionary.type_id == p_dict_type_id).all()
    for i in diction:
        res_arr.append((i['id'], i['description']))
    return res_arr


def get_emp_id_by_session(p_ip):
    dt = datetime.now()
    sql_check = db.select(Sessions.emp_id).where(
        db.and_(Sessions.ip_connect == f'{p_ip}', Sessions.dt_session_logout > dt))
    res = db.session.execute(sql_check).fetchone()
    return res


# Получить список всех заявок, входной параметр - к-во записей
def get_app_list(p_count_row=0):
    res_arr = []
    if p_count_row == "0":
        app_all = db.session.query(Application,
                                   Telegram_users).outerjoin(Telegram_users).where(Application.executor_id == 1).all()

    else:
        app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
            Application.executor_id == 1).limit(p_count_row).all()

    for application, users in app_all:
        res_arr.append((application.id, application.dt_add, application.type, application.description,
                       application.status, application.code, application.creator_id, users.full_name,
                       application.dt_upd))
    return res_arr


def get_app_list_by_emp(p_count_row=0, p_emp_id=0):
    res_arr = []
    if p_count_row == "0":
        app_all = db.session.query(Application,
                                   Telegram_users).outerjoin(Telegram_users).where(
            Application.executor_id == p_emp_id).all()

    else:
        app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
            Application.executor_id == p_emp_id).limit(p_count_row).all()

    for application, users in app_all:
        res_arr.append((application.id, application.dt_add, application.type, application.description,
                        application.status, application.code, application.creator_id, users.full_name,
                        application.dt_upd))
    return res_arr

    # if p_count_row == 0:
    #     # app_all = db.session.query(Application).all()
    #     # app_all = db.session.query(Employees, Application).outerjoin(Application, Employees.id == Application.creator_id).all()
    #     app_all = db.session.query(Application, Employees).outerjoin(Employees,
    #                                Application.creator_id == Employees.id).all()
    # else:
    #     # app_all = db.session.query(Application).limit(p_count_row).all()
    #     app_all = db.session.query(Application, Employees).outerjoin(Employees,
    #                                Application.creator_id == Employees.id).limit(p_count_row).all()



# TELEGRAM
def autorization_telegram():
    pass


def create_user_telegram():
    pass
