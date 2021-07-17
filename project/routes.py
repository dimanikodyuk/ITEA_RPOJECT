from flask import render_template
from models import (my_apply, db, request, Departments, Employees, Dictionary, Dictionary_type, Log, Telegram_logs,
                    Telegram_users, Application, Sessions, check_dep, get_dep_list, create_log,
                    check_emp, check_emp, get_emp_list, get_dictionary_value_list, get_app_list,
                    get_emp_id_by_session, get_app_list_by_emp, get_comment_by_apply, add_comment)
from datetime import datetime


@my_apply.route('/', methods=["GET", "POST"])
@my_apply.route('/main', methods=["GET", "POST"])
def homepage():
    ip = request.environ['REMOTE_ADDR']
    res = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)

    if res is None:
        return render_template("index.html", emp_id=0)
    else:
        return render_template("index.html", emp_id=emp_id[0], user_role=res[0])


def check_active_session(p_ip_connect):
    dt = datetime.now()
    # Удаляем устаревшие сессии
    del_old_sess = db.delete(Sessions).where(Sessions.dt_session_logout < dt)
    db.session.execute(del_old_sess)
    db.session.commit()
    # Проверяем активную сессию

    sql_check = db.select(Sessions.role_id, Sessions.emp_id).where(
        db.and_(Sessions.ip_connect == f'{p_ip_connect}', Sessions.dt_session_logout > dt))
    res = db.session.execute(sql_check).fetchone()
    return res


def create_session(p_ip_connect, p_user_roles, p_login):
    dt = datetime.now()

    sql_dep = db.select(Employees.id).where(Employees.login == f'{p_login}')
    res = db.session.execute(sql_dep).fetchone()

    cr_session = Sessions(ip_connect=p_ip_connect, dt_add=dt, role_id=p_user_roles, emp_id=res[0])
    db.session.add(cr_session)
    db.session.commit()


@my_apply.route("/authorization", methods=["GET", "POST"])
def authorization():

    #  Считываем логин и пароль с формы сайта
    inp_login = request.form.get('inp_login')
    inp_pass = request.form.get('inp_pass')
    ip_conn = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip_conn)
    print(res_session)
    # Если за указанным IP адрессом есть активная сессия
    if res_session is None:
        if request.method == "POST":

            # Проверяем сперва сотрудник ли это
            sql_emp = db.select(Employees.id).where(
                db.and_(Employees.login == f'{inp_login}', Employees.password == f'{inp_pass}'))
            res_emp = db.session.execute(sql_emp).fetchone()
            # Если ничего не найдено, то ищем в таблице клиентов
            if res_emp is None:
                sql_client = db.select(Telegram_users.id).where(
                    db.and_(Telegram_users.nickname == f'{inp_login}', Telegram_users.password == f'{inp_pass}'))
                res_cl = db.session.execute(sql_client).fetchone()

                if res_cl is None:
                    return render_template("authorization.html", res_txt="Ошибка авторизации. Проверьте данные.")
                else:
                    # Права пользователя
                    user_roles = 3
                    create_session(ip_conn, user_roles, inp_login)
                    return render_template("authorization.html", res_txt="Авторизация прошла успешно",
                                           user_role=user_roles)
            else:
                # Права сотрудника
                user_roles = 2
                create_session(ip_conn, user_roles, inp_login)

                return render_template("authorization.html", res_txt="Авторизация прошла успешно", user_role=user_roles)
        else:
            return render_template("authorization.html")
    else:
        return render_template("authorization.html", res_txt="Вы уже авторизованы, у вас есть активная сессия",
                               user_role=res_session[0])


# Создание нового департамента
@my_apply.route("/create_dep", methods=["POST"])
def create_dep():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)

    dep_name = request.form.get('dep_name')
    if dep_name is not None:
        dt = datetime.now()
        ch_dep = check_dep(1, dep_name)
        if ch_dep is not None:
            return render_template("departments_add.html", dep_list="", emp_id=emp_id[0],
                                   dep_data="В системе уже есть департамент с таким именем", user_roles=res_session[0])
        else:
            dep_cr = Departments(dt_add=dt, dep_name=dep_name, dt_upd=dt)
            db.session.add(dep_cr)
            db.session.flush()
            db.session.commit()

            source = "/create_dep"
            log_text = f"Добавлен департамент с именем dep_name: {dep_name}"
            create_log(source, log_text)

            return render_template("departments_add.html", dep_list="", emp_id=emp_id[0], dep_data=log_text,
                                   user_roles=res_session[0])
    return render_template("departments_add.html", dep_list="", dep_data="", emp_id=0, user_roles=res_session[0])


# Обновление департамента по id
@my_apply.route("/update_dep", methods=["POST"])
def update_dep():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)

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

        source = "/update_dep"
        log_text = f"Изменено название департамента с id {old_dep_id} на {new_dep_name}"
        create_log(source, log_text)

        res_txt = f"Успешно обновлено название департамента с id {old_dep_id} на {new_dep_name}"
        return render_template("departments_update.html", dep_list=dep_list, dep_data=res_txt,
                               emp_id=emp_id[0], user_roles=res_session[0])
    else:
        return render_template("departments_update.html", emp_id=emp_id[0], dep_list=dep_list, dep_data="",
                               user_roles=res_session[0])


# Удаление департамента
@my_apply.route("/delete_dep", methods=["POST"])
def delete_dep_by_id():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)

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

            return render_template("departments_delete.html", dep_list=dep_list, emp_id=emp_id[0], dep_data=log_text,
                                   user_roles=res_session[0])
        return render_template("departments_delete.html", dep_list=dep_list, emp_id=emp_id[0], dep_data="",
                               user_roles=res_session[0])
    else:
        return render_template("departments_delete.html", dep_list="", dep_data="", emp_id=0, user_roles="")


# Получение всех департаментов
@my_apply.route("/get_all_dep", methods=["GET", "POST"])
def get_all_dep():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)
    if res_session is None:
        return render_template("departments.html", dep_list="", emp_id=0, dep_data="Вы не авторизированы",
                               user_roles="")
    else:
        cou_row = request.form.get('cou_row')
        if cou_row == "0":
            dep_list = get_dep_list()
        else:
            dep_list = get_dep_list(cou_row)
        return render_template("departments.html", dep_list=dep_list, emp_id=emp_id[0], user_roles=res_session[0])


# Создание сотрудника
@my_apply.route("/create_emp", methods=["POST"])
def create_emp():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)
    if res_session is None:
        return render_template("employees_add.html", emp_result="", occupation="", emp_id=emp_id[0], departments="",
                               user_roles="")
    else:
        dict_occupation = get_dictionary_value_list(1)
        dict_departments = get_dep_list()

        full_name = request.form.get('full_name')
        position = request.form.get('position')
        departments = request.form.get('departments')
        login = request.form.get('login')

        if full_name is not None:
            dt = datetime.now()
            check_employees = check_emp(1, full_name)
            if check_employees is not None:
                return render_template("employees_add.html",
                                       emp_result=f"Сотрудник с таким ФИО уже существует, его id: {check_employees}",
                                       occupation="", departments="", emp_id=emp_id[0], user_roles=res_session[0])
            else:
                emp_create = Employees(dt_add=dt, full_name=full_name, position=position, department_id=departments,
                                       login=login, password=11111111, dt_update=dt)
                db.session.add(emp_create)
                db.session.flush()

                source = "/create_emp"
                log_text = f"Создан сотрудник с ФИО {full_name}, login: {login}"
                create_log(source, log_text)
                db.session.commit()

                return render_template("employees_add.html", emp_result="Добавлен новый сотрудник")

        return render_template("employees_add.html", emp_result="", emp_id=emp_id[0], occupation=dict_occupation,
                               departments=dict_departments, user_roles=res_session[0])


# Обновление данных сотрудника
@my_apply.route("/update_emp", methods=["POST"])
def update_emp():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_ids = get_emp_id_by_session(ip)
    dict_occupation = get_dictionary_value_list(1)
    dict_departments = get_dep_list()
    dict_employees = get_emp_list()

    emp_id = request.form.get('old_emp_data')
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    departments = request.form.get('departments')
    login = request.form.get('login')

    if res_session is not None:
        check_employeer = check_emp(2, emp_id)
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
                                   departments=dict_departments, emp_id=emp_ids[0], employees_list=dict_employees,
                                   user_roles=res_session[0])
        return render_template("employees_update.html", emp_result="", occupation=dict_occupation, emp_id=emp_ids[0],
                               departments=dict_departments, employees_list=dict_employees, user_roles=res_session[0])
    else:
        return render_template("employees_update.html", emp_result="Вы не авторизированы", occupation="",
                               departments="", employees_list="", emp_id=0, user_roles="")


# Удаление сотрудника
@my_apply.route("/delete_emp", methods=["POST"])
def delete_emp():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_ids = get_emp_id_by_session(ip)

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

            return render_template("employees_delete.html", emp_result=log_text, employees_list=emp_list,
                                   emp_id=emp_ids[0], user_roles=res_session[0])

        return render_template("employees_delete.html", emp_result="", employees_list=emp_list,
                               emp_id=emp_ids[0], user_roles=res_session[0])
    else:
        return render_template("employees_delete.html", emp_result="Выберите сотрудника для удаления",
                               emp_id=emp_ids[0], employees_list=emp_list, user_roles="")


# Получение данных всех сотрудников
@my_apply.route("/get_all_emp", methods=["GET", "POST"])
def get_all_emp():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_ids = get_emp_id_by_session(ip)
    if res_session is None:
        return render_template("employees.html", employees_list="", user_roles="", emp_result="Вы не авторизированы")
    else:
        cou_row = request.form.get('cou_row')
        if cou_row == "0":
            emp_list = get_emp_list()
        else:
            emp_list = get_emp_list(cou_row)
        return render_template("employees.html", employees_list=emp_list, emp_id=emp_ids[0],
                               user_roles=res_session[0], emp_result="")


# Полученние списка всех заявок
@my_apply.route("/get_all_app", methods=["GET", "POST"])
def get_all_app():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_ids = get_emp_id_by_session(ip)

    if res_session is None:
        return render_template("applications.html", employees_list="", filt_value=0, user_roles="",
                               emp_result="Вы не авторизированы")
    else:
        app_list = []
        cou_row = request.form.get('cou_row')
        filter = request.form.get('filter')
        filter_val = request.form.get('filter_val')

        if cou_row == "0" and filter is None:
            app_list = get_app_list("0", -1, 0)
        elif cou_row != "0" and filter is None:
            app_list = get_app_list(cou_row, -1, 0)
        elif cou_row == "0" and filter is not None:
            app_list = get_app_list("0", filter, filter_val)
        elif cou_row != "0" and filter is not None:
            app_list = get_app_list(cou_row, filter, filter_val)

        return render_template("applications.html", app_list=app_list,
                               apply_info="", emp_id=emp_ids[0], user_roles=res_session[0])


# Функция принятия заявки в роботу
@my_apply.route("/set_executor_apply/<int:app_id>", methods=["POST"])
def set_executor_apply(app_id):
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)

    if res_session is not None:
        sql_app = db.select(Application.id).where(Application.id == f'{app_id}')
        res = db.session.execute(sql_app).fetchone()

        app = Application.query.get(res)

        app.executor_id = emp_id[0]
        app.status = "В роботе"
        db.session.commit()

        source = "/update_emp"
        log_text = f"Обновлен сотрудник по заявке: {app} на {emp_id[0]}"
        create_log(source, log_text)

        app_list = get_app_list()

        return render_template("applications.html", app_list=app_list, apply_info="Заявку взято в роботу",
                               emp_id=emp_id[0], user_roles=res_session[0])
    else:
        return render_template("applications.html", app_list="", apply_info="", emp_id=0, user_roles="")


# Вывод списка моих заявок
@my_apply.route("/my_app", methods=["GET", "POST"])
def my_app():
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_ids = get_emp_id_by_session(ip)

    if res_session is None:
        return render_template("applications_by_emp.html", employees_list="", user_roles="",
                               emp_result="Вы не авторизированы")
    else:
        cou_row = request.form.get('cou_row')
        if cou_row == "0":
            app_list = get_app_list_by_emp(cou_row, emp_ids[0])
        else:
            app_list = get_app_list_by_emp(cou_row, emp_ids[0])
        return render_template("applications_by_emp.html", app_list=app_list, apply_info="", emp_id=emp_ids[0],
                               user_roles=res_session[0])


# Просмотр и написание комментариев по заявке
@my_apply.route("/view_apply/<int:app_id>", methods=["POST"])
def view_apply(app_id):
    ip = request.environ['REMOTE_ADDR']
    res_session = check_active_session(ip)
    emp_id = get_emp_id_by_session(ip)
    print(app_id)
    if res_session is not None:

        comm = request.form.get('comm_text')
        if comm is not None:
            add_comment(app_id, emp_id[0], 999999, comm)

        comm_list = get_comment_by_apply(app_id)

        return render_template("applications_comment.html", app_list=comm_list, apply_info="Заявку взято в роботу",
                               emp_id=emp_id[0], user_roles=res_session[0])
    else:
        return render_template("applications_comment.html", app_list="", apply_info="", emp_id=0, user_roles="")
