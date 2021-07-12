from datetime import datetime
from telebot import TeleBot, types
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
from models import my_apply, db, Departments, Employees, Dictionary, Dictionary_type, Log, Telegram_logs, Telegram_users, Customers, Sessions, check_dep_name\
    , check_dep_id, get_dep_list, create_log, check_emp_id, check_emp, get_emp_list, get_dictionary_value_list
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

# Создание нового департамента
@my_apply.route("/create_dep", methods=["POST"])
def create_dep():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    dep_name = request.form.get('dep_name')
    print("DEP_NAME: ", dep_name)
    if dep_name is not None:
        dt = datetime.now()
        check_dep = check_dep_name(dep_name)
        if check_dep is not None:
            return render_template("departments_add.html", dep_list="", dep_data="В системе уже есть департамент с таким именем", user_roles=res_session[0])
            print("Ура, мы получили название департамента")
            print("Результат проверки: ", check_dep)
        else:
            dep_cr = Departments(dt_add=dt, dep_name=dep_name, dt_upd=dt)
            db.session.add(dep_cr)
            db.session.flush()

            source = "/create_dep"
            log_text = f"Добавлен департамент с именем dep_name: {dep_name}"
            create_log(source, log_text)

            return render_template("departments_add.html", dep_list="", dep_data=log_text, user_roles=res_session[0])
    return render_template("departments_add.html", dep_list="", dep_data="", user_roles=res_session[0])

# Обновление департамента по id
@my_apply.route("/update_dep", methods=["POST"])
def update_dep():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])

    dep_list = get_dep_list()
    print("DEP_LIST:", dep_list)
    old_dep_id = request.form.get('old_dep_name')
    new_dep_name = request.form.get('new_dep_name')

    if new_dep_name is not None:
        dt = datetime.now()

        dep = Departments.query.get(old_dep_id)
        dep.dep_name = new_dep_name
        dep.dt_upd = dt
        db.session.flush()

        source="/update_dep"
        log_text = f"Изменено название департамента с id {old_dep_id} на {new_dep_name}"
        create_log(source, log_text)

        res_txt = f"Успешно обновлено название департамента с id {old_dep_id} на {new_dep_name}"
        return render_template("departments_update.html", dep_list=dep_list, dep_data=res_txt, user_roles=res_session[0])
    else:
        return render_template("departments_update.html", dep_list=dep_list, dep_data="", user_roles=res_session[0])

@my_apply.route("/delete_dep", methods=["POST"])
def delete_dep_by_id():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    if res_session is not None:
        dep_list = get_dep_list()

        dep_id = request.form.get('del_dep_name')
        if dep_id is not None:
            dep = Departments.query.get(dep_id)
            db.session.delete(dep)
            db.session.commit()

            source = "/delete_dep"
            log_text = f"Удалён департамент с id {dep_id}"
            create_log(source, log_text)

            return render_template("departments_delete.html", dep_list=dep_list, dep_data=log_text, user_roles=res_session[0])
    else:
        return render_template("departments_delete.html", dep_list=dep_list, dep_data="", user_roles=res_session[0])

@my_apply.route("/get_all_dep", methods=["GET", "POST"])
def get_all_dep():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    if res_session is None:
        return render_template("departments.html", dep_list="", dep_data="Вы не авторизированы", user_roles="")
    else:
        cou_row = request.form.get('cou_row')

        if cou_row == "0":
            dep_list = get_dep_list()
        else:
            dep_list = get_dep_list(cou_row)
        return render_template("departments.html", dep_list=dep_list, user_roles=res_session[0])

@my_apply.route("/create_emp", methods=["POST"])
def create_emp():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    if res_session is None:
        return render_template("employees_add.html", emp_result="", occupation="", departments="", user_roles="")
    else:
        dict_occupation = get_dictionary_value_list(1)
        dict_departments = get_dep_list()

        full_name = request.form.get('full_name')
        position = request.form.get('position')
        departments = request.form.get('departments')
        login = request.form.get('login')

        if full_name is not None:
            dt = datetime.now()
            check_employees = check_emp(full_name)

            if check_employees is not None:
                return render_template("employee.employees_add",
                                       emp_result=f"Сотрудник с таким ФИО уже существует, его id: {check_employees}"
                                       , occupation="", departments="", user_roles=res_session[0])
            else:
                emp_create = Employees(dt_add=dt, full_name=full_name, position=position, department_id=departments, login=login,
                                   password=11111111, dt_update=dt)
                db.session.add(emp_create)
                db.session.flush()

                source = "/create_emp"
                log_text = f"Создан сотрудник с ФИО {full_name}, login: {login}"
                create_log(source, log_text)
                db.session.commit()

                return render_template("employees_add.html", emp_result="Добавлен новый сотрудник")

        return render_template("employees_add.html", emp_result="", occupation=dict_occupation,
                               departments=dict_departments, user_roles=res_session[0])

@my_apply.route("/update_emp", methods=["POST"])
def update_emp():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    dict_occupation = get_dictionary_value_list(1)
    dict_departments = get_dep_list()
    dict_employees = get_emp_list()

    emp_id = request.form.get('old_emp_data')
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    departments = request.form.get('departments')
    login = request.form.get('login')

    if res_session is not None:
        check_employeer = check_emp_id(emp_id)
        if check_employeer is not None:
            # запрос в БД
            emp = Employees.query.get(check_employeer)

            emp.full_name = full_name
            emp.position = position
            emp.department_id = departments
            emp.login = login
            db.session.commit()

            source = "/update_emp"
            log_text = f"Обновлен сотрёдник с id {emp_id}"
            create_log(source, log_text)
            return render_template("employees_update.html", emp_result=log_text, occupation=dict_occupation,
                                   departments=dict_departments, employees_list=dict_employees,
                                   user_roles=res_session[0])
        return render_template("employees_update.html", emp_result="", occupation=dict_occupation,
                               departments=dict_departments, employees_list=dict_employees, user_roles=res_session[0])
    else:
        return render_template("employees_update.html", emp_result="Вы не авторизированы", occupation="", departments="", employees_list="",
                               user_roles="")

@my_apply.route("/delete_emp", methods=["POST"])
def delete_emp():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    emp_list = get_emp_list()

    if res_session is not None:
        emp_id = request.form.get('del_emp_id')

        if emp_id is not None:
            emp = Employees.query.get(emp_id)
            db.session.delete(emp)
            db.session.commit()

            source = "/delete_emp"
            log_text = f"Удалён сотрудник с id {emp_id}"
            create_log(source, log_text)

            return render_template("employees_delete.html", emp_result=log_text, employees_list=emp_list, user_roles=res_session[0])

        return render_template("employees_delete.html", emp_result="", employees_list=emp_list, user_roles=res_session[0])
    else:
        return render_template("employees_delete.html", emp_result="Выберите сотрудника для удаления", employees_list=emp_list, user_roles=res_session[0])

@my_apply.route("/get_all_emp", methods=["GET", "POST"])
def get_all_emp():
    res_session = check_active_session(request.environ['REMOTE_ADDR'])
    if res_session is None:
        return render_template("employees.html", employees_list="", user_roles="", emp_result="Вы не авторизированы")
    else:
        cou_row = request.form.get('cou_row')
        if cou_row == "0":
            emp_list = get_emp_list()
        else:
            emp_list = get_emp_list(cou_row)
        return render_template("employees.html", employees_list=emp_list, user_roles=res_session[0], emp_result="")


my_apply.run(debug=True)