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

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Имя: {self.name}
    Описание: {self.description}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
        ---------------------------------------------------
        Имя: {self.name}
        Описание: {self.description}
        ---------------------------------------------------
        '''
        return res


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('dictionary_type.id', ondelete='SET NULL'), nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    Код: {self.code}
    Описание: {self.description}
    Тип: {self.type_id}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            Код: {self.code}
            Описание: {self.description}
            Тип: {self.type_id}
            ---------------------------------------------------
            '''
        return res


class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    dep_name = db.Column(db.String(100), nullable=False)
    dt_upd = db.Column(db.DateTime, nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    Название: {self.dep_name}
    Дата обновления: {self.dt_upd}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            Название: {self.dep_name}
            Дата обновления: {self.dt_upd}
            ---------------------------------------------------
            '''
        return res


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    position = db.Column(db.Integer, db.ForeignKey('dictionary.id', ondelete='SET NULL'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    dt_upd = db.Column(db.DateTime, nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    ФИО: {self.full_name}
    Должность: {self.position}
    Департамент: {self.department_id}
    Логин: {self.login}
    Пароль: {self.password}
    Дата обновления: {self.dt_upd}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            ФИО: {self.full_name}
            Должность: {self.position}
            Департамент: {self.department_id}
            Логин: {self.login}
            Пароль: {self.password}
            Дата обновления: {self.dt_upd}
            ---------------------------------------------------
            '''


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    Тип: {self.source}
    Комментарий: {self.comment}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            Тип: {self.source}
            Комментарий: {self.comment}
            ---------------------------------------------------
            '''
        return res


class Telegram_logs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(100), nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    Ник: {self.nickname}
    Чат id: {self.chat_id}
    Сообщение: {self.message}
    Тип: {self.type}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            Ник: {self.nickname}
            Чат id: {self.chat_id}
            Сообщение: {self.message}
            Тип: {self.type}
            ---------------------------------------------------
            '''
        return res

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

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    ФИО: {self.full_name}
    Чат id: {self.chat_id}
    Ник: {self.nickname}
    Пароль: {self.password}
    Роль: {self.role}
    Телефон: {self.phone}
    Подпись на уведомления: {self.is_subscribed}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            ФИО: {self.full_name}
            Чат id: {self.chat_id}
            Ник: {self.nickname}
            Пароль: {self.password}
            Роль: {self.role}
            Телефон: {self.phone}
            Подпись на уведомления: {self.is_subscribed}
            ---------------------------------------------------
            '''
        return res


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_connect = db.Column(db.String(100), nullable=False)
    dt_add = db.Column(db.DateTime, nullable=False)
    dt_session_logout = db.Column(db.DateTime, nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    IP адресс: {self.source}
    Дата добавления: {self.dt_add}
    Дата окончания сессии: {self.comment}
    Роль: {self.comment}
    ID сотрудника: {self.comment}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            IP адресс: {self.source}
            Дата добавления: {self.dt_add}
            Дата окончания сессии: {self.comment}
            Роль: {self.comment}
            ID сотрудника: {self.comment}
            ---------------------------------------------------
            '''
        return res

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

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    Тип: {self.type}
    Описание: {self.description}
    Статус: {self.status}
    Код: {self.code}
    ID автора: {self.creator_id}
    ID исполнителя: {self.executor_id}
    Дата обновления: {self.dt_upd}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            Тип: {self.type}
            Описание: {self.description}
            Статус: {self.status}
            Код: {self.code}
            ID автора: {self.creator_id}
            ID исполнителя: {self.executor_id}
            Дата обновления: {self.dt_upd}
            ---------------------------------------------------
            '''
        return res

class Application_comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dt_add = db.Column(db.DateTime, nullable=False)
    telegram_user_id = db.Column(db.Integer, db.ForeignKey('telegram_users.id', ondelete='SET NULL'), nullable=False)
    employees_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='SET NULL'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('application.id', ondelete='SET NULL'), nullable=False)

    def __str__(self):
        res = f'''id: {self.id}
    ---------------------------------------------------
    Дата добавления: {self.dt_add}
    ID пользователя телеграм: {self.telegram_user_id}
    ID сотрудника: {self.employees_id}
    Комментарий: {self.comment}
    ID заявки: {self.app_id}
    ---------------------------------------------------
    '''
        return res

    def __repr__(self):
        res = f'''id: {self.id}
            ---------------------------------------------------
            Дата добавления: {self.dt_add}
            ID пользователя телеграм: {self.telegram_user_id}
            ID сотрудника: {self.employees_id}
            Комментарий: {self.comment}
            ID заявки: {self.app_id}
            ---------------------------------------------------
            '''
        return res

# Очистка всех сессий (таблица crm.sessions)
db.session.query(Sessions).delete()
db.session.commit()


def create_log(p_source, p_comment):
    dt = datetime.now()
    log = Log(dt_add=dt, source=p_source, comment=p_comment)
    db.session.add(log)
    db.session.commit()


def telegram_logs(p_nickname, p_chat_id, p_message, p_type):
    dt = datetime.now()
    log = Telegram_logs(dt_add=dt, nickname=p_nickname, chat_id=p_chat_id, message=p_message, type=p_type)
    db.session.add(log)
    db.session.commit()


# Проверка наличия департамента в БД
def check_dep(p_type, p_val):
    if p_type == 1:
        sql_dep = db.select(Departments.id).where(Departments.dep_name == f'{p_val}')
    else:
        sql_dep = db.select(Departments.id).where(Departments.id == f'{p_val}')
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
def check_emp(p_type, p_val):
    if p_type == 1:
        sql_dep = db.select(Employees.id).where(Employees.full_name == f'{p_val}')
    else:
        sql_dep = db.select(Employees.id).where(Employees.id == f'{p_val}')
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


# Вывод значений словаря по type_id
def get_dictionary_value_list(p_dict_type_id):
    res_arr = []
    diction = db.session.query(Dictionary.id, Dictionary.description).filter(Dictionary.type_id == p_dict_type_id).all()
    for i in diction:
        res_arr.append((i['id'], i['description']))
    return res_arr


# Получения id сотрудника по ІР сессии
def get_emp_id_by_session(p_ip):
    dt = datetime.now()
    sql_check = db.select(Sessions.emp_id).where(
        db.and_(Sessions.ip_connect == f'{p_ip}', Sessions.dt_session_logout > dt))
    res = db.session.execute(sql_check).fetchone()
    return res


# Получить все заявки
def get_app_list(p_count_row=0, p_filter_id=-1, p_filter_value=-1):
    res_arr = []
    app_all = 0
    if p_count_row == "0":

        if p_filter_id == -1:
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
                                        Application.executor_id == 1).all()
        elif p_filter_id == "0":
            print("P_FILTER_VALUE 0: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).filter(
                                        Telegram_users.full_name.like('%'+p_filter_value+'%')).all()
        elif p_filter_id == "1":
            print("P_FILTER_VALUE 1: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).filter(
                                        Application.status.like('%'+p_filter_value+'%')).all()
        elif p_filter_id == "2":
            print("P_FILTER_VALUE 2: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
                                        Application.executor_id == p_filter_value).all()

    elif p_count_row != "0":
        if p_filter_id == -1:
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
                                        Application.executor_id == 1).limit(p_count_row).all()
        elif p_filter_id == "0":
            print("P_FILTER_VALUE 0_0: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
                                        Telegram_users.full_name.like('%'+p_filter_value+'%')).limit(p_count_row).all()
        elif p_filter_id == "1":
            print("P_FILTER_VALUE 1_1: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).filter(
                                        Application.status.like('%'+p_filter_value+'%')).limit(p_count_row).all()
        elif p_filter_id == "2":
            print("P_FILTER_VALUE 2_2: ", p_filter_value)
            app_all = db.session.query(Application, Telegram_users).outerjoin(Telegram_users).where(
                                        Application.executor_id == p_filter_value).limit(p_count_row).all()

    for application, users in app_all:
        res_arr.append((application.id, application.dt_add, application.type, application.description,
                       application.status, application.code, application.creator_id, users.full_name,
                       application.dt_upd))
    return res_arr


# Получить заявки по определенному сотруднику
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


# Получить комментарии по заявке
def get_comment_by_apply(p_apply_id):
    res_arr = []
    app = db.session.query(Application_comment, Telegram_users).outerjoin(Telegram_users).where(db.and_(db.or_(
        Telegram_users.id == Application_comment.telegram_user_id, Application_comment.employees_id == 1),
        Application_comment.app_id == p_apply_id))

    for ap, client in app:
        res_arr.append((ap.id, ap.dt_add, ap.comment, client.full_name, ap.employees_id))
    return res_arr


# Добавить комментарий к заявке
def add_comment(p_app_id, p_emp_id, p_telegram_user_id, p_comment):
    dt = datetime.now()
    ad_comm = Application_comment(app_id=p_app_id, dt_add=dt, telegram_user_id=p_telegram_user_id,
                                  employees_id=p_emp_id, comment=p_comment)
    db.session.add(ad_comm)
    db.session.commit()
