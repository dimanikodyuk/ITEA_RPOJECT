from datetime import datetime
from telebot import TeleBot, types
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
from models import my_apply, db, Departments, Employees, Dictionary, Dictionary_type, Log, Telegram_logs, Telegram_users, Customers, Sessions
import uuid

# Очистка всех сессий (таблица crm.sessions)
db.session.query(Sessions).delete()
db.session.commit()


@my_apply.route('/', methods=["GET", "POST"])
@my_apply.route('/main', methods=["GET", "POST"])
def homepage():
    res = check_active_session(request.environ['REMOTE_ADDR'])
    if res is None:
        return render_template("index.html")
    else:
        return render_template("index.html", user_role=res[0])


def check_active_session(p_ip_connect):
    dt = datetime.now()
    # Удаляем устаревшие сессии
    del_old_sess = db.delete(Sessions).where(Sessions.dt_session_logout < f'{dt}')
    db.session.execute(del_old_sess)
    db.session.commit()
    # Проверяем активную сессию
    sql_check = db.select(Sessions.role_id).where(db.and_(Sessions.ip_connect == f'{p_ip_connect}', Sessions.dt_session_logout > f'{dt}'))
    res = db.session.execute(sql_check).fetchone()
    return res


@my_apply.route("/autorization", methods=["GET", "POST"])
def autorization():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    print(res_session)
    # Если за указанным IP адрессом есть активная сессия
    if res_session is None:
        if request.method == "POST":
            # Переменная с правами из таблички crm.dictionary
            user_role = 0
            #  Считываем логин и пароль с формы сайта
            inp_login = request.form.get('inp_login')
            inp_pass = request.form.get('inp_pass')

            # Проверяем сперва сотрудник ли это
            sql_emp = db.select(Employees.id).where(db.and_(Employees.login == f'{inp_login}', Employees.password == f'{inp_pass}'))
            res_emp = db.session.execute(sql_emp).fetchone()

            # Если ничего не найдено, то ищем в таблице клиентов
            if res_emp is None:
                sql_client = db.select(Telegram_users.id).where(db.and_(Telegram_users.nickname == f'{inp_login}', Telegram_users.password == f'{inp_pass}'))
                res_cl = db.session.execute(sql_client).fetchone()

                if res_cl is None:
                    return render_template("autorization.html", res_txt= "Ошибка авторизации. Проверьте данные.")
                else:
                    # Права пользователя
                    user_roles = 3
                    dt = datetime.now()
                    cr_session = Sessions(ip_connect=request.environ['REMOTE_ADDR'], dt_add=dt, role_id=user_roles)
                    db.session.add(cr_session)
                    db.session.commit()
                    return render_template("autorization.html", res_txt= "Авторизация прошла успешно", user_role = user_roles)
            else:
                # Права сотрудника
                user_roles = 2
                dt = datetime.now()
                cr_session = Sessions(ip_connect=request.environ['REMOTE_ADDR'], dt_add=dt, role_id=user_roles)
                db.session.add(cr_session)
                db.session.commit()

                return render_template("autorization.html", res_txt="Авторизация прошла успешно", user_role=user_roles)

        else:
            return render_template("autorization.html")
    else:
        return render_template("autorization.html", res_txt="Вы уже авторизованы, у вас есть активная сессия", user_role=res_session[0])


# Проверка наличия департамента в БД
def check_dep_name(p_dep_name):
    # запрос в БД
    sql_dep = db.select(Departments.id).where(Departments.dep_name == f'{p_dep_name}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res

def check_dep_id(p_dep_id):
    # запрос в БД
    sql_dep = db.select(Departments.id).where(Departments.id == f'{p_dep_id}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res

# Создание нового департамента
@my_apply.route("/create_dep", methods=["POST"])
def create_dep():

    if request.method == "POST":
        dep_data = json.loads(request.data)
        dep_name = dep_data["department_name"]

        res = check_dep_name(dep_name)

        if res is None:
            dep_cr = Departments(department_name=dep_name)
            db.session.add(dep_cr)
            db.session.flush()

            dt = datetime.now()
            log_text = f"Добавлен департамент с параметрами dep_name:{dep_name}"
            log = Log(created_dt=dt, type="create_apl", comment=log_text)
            db.session.add(log)
            db.session.flush()

            db.session.commit()

            return render_template("change_department.html", dep_data=dep_data)
        else:
            return render_template("change_department.html", dep_data={"ОШИБКА: Департамент уже существует"})

# Обновление департамента по id
@my_apply.route("/update_dep", methods=["POST"])
def update_dep_by_name():
    if request.method == "POST":
        dep_data = json.loads(request.data)
        dep_name_old = dep_data["department_name_old"]
        dep_name_new = dep_data["department_name_new"]

        res = check_dep_name(dep_name_old)
        if res is None:
            return render_template("departments.html", dep_data="ОШИБКА: Департамент не существует")
        else:

            # запрос в БД
            dep = Departments.query.get(res[0])
            dep.department_name = dep_name_new
            db.session.commit()

            #sql_dep = db.update(Departments).where(Departments.department_id == f'{res[0]}').values(Departments.department_name == f'{dep_name_new}')
            #print(sql_dep)

            dt = datetime.now()
            log_text = f"Обновлён департамент с id {res[0]}."
            log = Log(created_dt=dt, type="update_dep", comment=log_text)
            db.session.add(log)
            db.session.flush()
            db.session.commit()

            return render_template("departments.html", dep_data=f"ИНФО: Обновлено департамент id {res[0]}. Новое имя {dep_name_new}")

@my_apply.route("/delete_dep/<int:dep_id>", methods=["DELETE"])
def delete_dep_by_id(dep_id):
    if request.method == "DELETE":
        res = check_dep_id(dep_id)
        if res is None:
            return render_template("change_department.html", dep_data=f"ОШИБКА: Подразделения с таким id не существует")
        else:
            dep = Departments.query.get(res[0])
            db.session.delete(dep)
            db.session.commit()
            return render_template("change_department.html", dep_data=f"ИНФО: Удалён департамент с id {dep_id}")

@my_apply.route("/get_all_dep", methods=["GET", "POST"])
def get_all_dep():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    if res_session is None:
        return render_template("departments.html", dep_list="", user_roles="")
    else:
        cou_row = request.form.get('cou_row')
        print("COU_ROW: ", cou_row)
        if cou_row == "0":
            rec = db.session.query(Departments).all()
            print("REC: ", rec)
        else:
            rec = db.session.query(Departments).limit(cou_row).all()
        res_arr_a = []
        for i in rec:
            res_arr_a.append((i.__dict__['id'], i.__dict__['dep_name']))
        return render_template("departments.html", dep_list=res_arr_a, user_roles=res_session[0])


def check_emp(p_fio):
    # запрос в БД
    sql_dep = db.select(Employees.id).where(Employees.full_name == f'{p_fio}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res

def check_emp_id(p_emp_id):
    # запрос в БД
    sql_dep = db.select(Employees.id).where(Employees.id == f'{p_emp_id}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res

@my_apply.route("/create_emp", methods=["POST"])
def create_emp():
    if request.method == "POST":
        emp_data = json.loads(request.data)

        fio = emp_data['fio']
        position = emp_data['position']
        dep_id = emp_data['dep_id']

        res = check_emp(fio)

        if res is None:

            emp_cr = Employees(fio=fio, position=position, department_id=dep_id)
            db.session.add(emp_cr)
            db.session.flush()

            dt = datetime.now()
            log_text = f"Добавлен сотрудник с параметрами fio:{fio}, position {position}, dep_id {dep_id}"
            log = Log(created_dt=dt, type="create_emp", comment=log_text)
            db.session.add(log)
            db.session.flush()
            db.session.commit()

            return render_template("employees.html", emp_result="ИНФО: Добавлен новый сотрудник")
        else:
            return render_template("employees.html", emp_result="ОШИБКА: Сотрудника не добавлено")

@my_apply.route("/update_emp", methods=["POST"])
def update_emp():
    if request.method == "POST":
        emp_data = json.loads(request.data)
        new_fio = emp_data["new_fio"]
        new_position = emp_data["new_position"]
        new_dep_id = emp_data["new_dep_id"]
        emp_id = emp_data["emp_id"]

        res = check_emp_id(emp_id)
        if res is None:
            return render_template("employees.html", emp_result="ОШИБКА: Сотрудник не найден")
        else:

            # запрос в БД
            emp = Employees.query.get(res[0])

            emp.fio = new_fio
            emp.position = new_position
            emp.department_id = new_dep_id

            db.session.commit()

            dt = datetime.now()
            log_text = f"Обновлён сотрудник с id {emp_id}, новые параметры fio:{new_fio}, position {new_position}, dep_id {new_dep_id}"
            log = Log(created_dt=dt, type="update_emp", comment=log_text)
            db.session.add(log)
            db.session.flush()
            db.session.commit()

            return render_template("employees.html", emp_result=f"ИНФО: Обновлено сотрудник id {emp_id}. Новое имя {new_fio}, должность: {new_position}, департамент: {new_dep_id}")

@my_apply.route("/delete_emp/<int:emp_id>", methods=["DELETE"])
def delete_emp(emp_id):
    if request.method == "DELETE":
        res = check_emp_id(emp_id)
        if res is None:
            return render_template("change_employees.html", emp_result=f"ОШИБКА: Сотрудника с таким id не существует")
        else:
            emp = Employees.query.get(res[0])
            db.session.delete(emp)
            db.session.commit()

            dt = datetime.now()
            log_text = f"Удалён сотрудник с id {emp_id}."
            log = Log(created_dt=dt, type="delete_emp", comment=log_text)
            db.session.add(log)
            db.session.flush()
            db.session.commit()

            return render_template("change_employees.html", emp_result=f"ИНФО: Удалён сотрудник с id {emp_id}")

@my_apply.route("/get_all_emp", methods=["GET", "POST"])
def get_all_emp():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])

    if res_session is None:
        return render_template("employees.html", employees_list="", user_roles="")
    else:
        cou_row = request.form.get('cou_row')
        if cou_row == "0":
            rec = db.session.query(Employees).all()
        else:
            rec = db.session.query(Employees).limit(cou_row).all()
        res_arr_a = []
        for i in rec:
            res_arr_a.append((i.__dict__['id'], i.__dict__['full_name'], i.__dict__['position'], i.__dict__['department_id']))
        return render_template("employees.html", employees_list=res_arr_a, user_roles=res_session[0])


my_apply.run(debug=True)