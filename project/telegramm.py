import uuid
from telebot import TeleBot, types
from config import TOKEN
from datetime import datetime
from models import (my_apply, db, Departments, Employees, Dictionary, Dictionary_type, Log, Telegram_logs,
                    Telegram_users, Application, Sessions, check_dep_name, check_dep_id, get_dep_list, create_log,
                    check_emp_id, check_emp, get_emp_list, get_dictionary_value_list, get_app_list)

bot = TeleBot(TOKEN)


# При авторизации у человека появится кнопка "Авторизация", при нажатии которой
# ему будет предложено поделиться номером телефона
def authorization(p_user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton('Авторизация', request_contact=True)])
    bot.send_message(p_user_id, """ Для продолжения нужна авторизация """, parse_mode="HTML", reply_markup=keyboard)


# Регистрация пользователя. Автоматически происходит подпись пользователя на рассылку новостей и прочего
def registration(p_chat_id, p_nickname, p_phone):
    dt = datetime.now()
    user_cr = Telegram_users(dt_add=dt, full_name="New", chat_id=p_chat_id, nickname=p_nickname,
                             role=1, phone=p_phone, password="12222", is_subscribed=1)
    db.session.add(user_cr)
    db.session.flush()
    db.session.commit()


def telegram_log(p_chat_id, p_nickname, p_message, p_type):
    dt = datetime.now()
    tel_log = Telegram_logs(dt_add=dt, nickname=p_nickname, chat_id=p_chat_id, message=p_message, type=p_type)
    db.session.add(tel_log)
    db.session.flush()
    db.session.commit()
    return "Add log"


# Когда человек заходит в бот и пишет /start (нажимает кнопку), переходим к авторизации
@bot.message_handler(commands=['start'])
def start(m):
    authorization(m.chat.id)


# Проверка пользователя на наличие в БД по номеру телефону
def check_tel_user_phone(p_phone):
    # запрос в БД
    sql_tel = db.select(Telegram_users.id).where(Telegram_users.phone == f'{p_phone}')
    # выполнение запроса
    res = db.session.execute(sql_tel).fetchone()
    return res


def check_tel_user_nickname(nickname):
    # запрос в БД
    sql_dep = db.select(Telegram_users.id).where(Telegram_users.nickname == f'{nickname}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res


# Меню которое отображается после авторизации/регистрации пользователем
def menu_user(p_user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton('Создать заявку')])
    keyboard.add(*[types.KeyboardButton('Созданные Вами заявки')])
    keyboard.add(*[types.KeyboardButton('Перейти на сайт')])
    bot.send_message(p_user_id, """ Сделайте Ваш выбор: """, parse_mode="HTML", reply_markup=keyboard)


# Логика которая отрабатывает после передачи номера телефона пользователем
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.from_user.username is None:
        user = "Неизвестный"
    else:
        user = message.from_user.username
    phone = message.contact.phone_number
    res = check_tel_user_phone(phone)
    new_res = check_tel_user_nickname(user)
    print(new_res)
    if res is None:
        registration(message.from_user.id, user, phone)
        bot.send_message(message.from_user.id, "Проводим регистрацию")

        # Обновление ФИО пользователя в БД
        msg = bot.reply_to(message, "Укажите Ваше ФИО:")
        bot.register_next_step_handler(msg, handle_check_fio)

    else:
        bot.send_message(message.from_user.id, "Авторизация прошла успешно. Добро пожаловать на наш сервис.")
        menu_user(message.from_user.id)


def handle_check_fio(message):
    full_name = message.text
    res = check_tel_user_nickname(message.from_user.username)
    user = Telegram_users.query.get(res[0])

    user.full_name = full_name
    db.session.commit()

    telegram_log(message.from_user.username, full_name, "", "Регистрация пользователя")

    msg = bot.reply_to(message, "Укажите пароль для входа на сайт:")
    bot.register_next_step_handler(msg, handler_check_pass)


def handler_check_pass(message):
    password = message.text

    res = check_tel_user_nickname(message.from_user.username)
    user = Telegram_users.query.get(res[0])

    user.password = password
    db.session.commit()

    bot.send_message(message.from_user.id, f"Спасибо за регистрацию. Добро пожаловать на наш сервис.")
    menu_user(message.from_user.id)


# Меню типов заявки
def type_order(p_user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton('Проблема')])
    keyboard.add(*[types.KeyboardButton('Консультация')])
    bot.send_message(p_user_id, """ Сделайте Ваш выбор: """, parse_mode="HTML", reply_markup=keyboard)


# Регистрация проблемы
def reg_app_problem(message):
    res = check_tel_user_nickname(message.from_user.username)
    if res is None:
        bot.send_message(message.from_user.id, "Произошла ошибка, обратитесь к администратору.")
    else:
        msg_text = message.text
        bot.send_message(message.from_user.id, f"Мы зарегестрировали Вашу проблему: {msg_text}")

        dt = datetime.now()
        # creator_id - это ид пользователя, который создает заявку
        # executor_id = 1 это заявка автоматически падает на админа, потом будет распределение
        apply = Application(dt_add=dt, type="Проблема", description=msg_text, status="New",
                            code=str(uuid.uuid4()), creator_id=res[0], executor_id=1)
        db.session.add(apply)
        db.session.flush()
        db.session.commit()

        type_app = "Регистрация проблемы"
        telegram_log(message.from_user.id, message.from_user.username, "", type_app)

        menu_user(message.from_user.id)


# Регистрация запроса на консультацию
def reg_app_consult(message):
    res = check_tel_user_nickname(message.from_user.username)
    if res is None:
        bot.send_message(message.from_user.id, "Произошла ошибка, обратитесь к администратору.")
    else:
        msg_text = message.text
        bot.send_message(message.from_user.id, f"Мы зарегестрировали Ваш запрос на консультацию по вопросу: {msg_text}")

        dt = datetime.now()
        apply = Application(dt_add=dt, type="Консультация", description=msg_text, status="New",
                            code=str(uuid.uuid4()), creator_id=res[0], executor_id=1)
        db.session.add(apply)
        db.session.flush()
        db.session.commit()

        type_app = "Регистрация заявки на консультацию"
        telegram_log(message.from_user.id, message.from_user.nickname, "", type_app)

        menu_user(message.from_user.id)


# Выбор типа проблемы
def reg_app(message):
    if message.text == "Проблема":
        msg = bot.reply_to(message, "Укажите суть проблемы:")
        bot.register_next_step_handler(msg, reg_app_problem)
    elif message.text == "Консультация":
        msg = bot.reply_to(message, "Укажите какая информация вас интересует:")
        bot.register_next_step_handler(msg, reg_app_consult)


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    if message.text == "Создать заявку":
        msg = bot.reply_to(message, "Выберите тип заявки:")
        type_order(message.from_user.id)
        bot.register_next_step_handler(msg, reg_app)
    elif message.text == "Созданные Вами заявки":
        res = check_tel_user_nickname(message.from_user.username)
        sql = db.select(Application.id, Application.dt_add, Application.status,
                        Application.executor_id).where(Application.creator_id == f'{res[0]}')
        res_db = db.session.execute(sql).fetchall()
        for row in res_db:
            if row[3] == 1 or row[3] is None:
                executor = 'Не назначен'
            else:
                executor = row[3]
            res_text = f"""
<b>Номер заявки в системе:</b> {row[0]}
<b>Дата создания:</b> {row[1]}
<b>Статус:</b> {row[2]}
<b>Ответственный:</b> {executor}
            """
            bot.send_message(message.from_user.id, res_text, parse_mode="HTML")
    elif message.text == "Перейти на сайт":
        bot.send_message(message.from_user.id, 'http://127.0.0.1:5000/')
    else:
        nick = message.from_user.username
        res = check_tel_user_nickname(nick)
        if res is None:
            res_text = f"""Неизвестная команда: {message.text} от незарегестрированного 
            пользователя: {message.from_user.username} с id: {message.from_user.id}"""
            telegram_log(message.from_user.id, message.from_user.nickname, "", res_text)
        else:
            bot.send_message(message.from_user.id, "Неизвестная команда")
            telegram_log(message.from_user.id, message.from_user.nickname, message.text, "Получено сообщение")


if __name__ == "__main__":
    # print("Telegram пользователи")
    # res_arr = []
    # user_all = db.session.query(Telegram_users).all()
    # for i in user_all:
    #     res_arr.append((i.__dict__['id'], i.__dict__['full_name']))
    # print(res_arr)

    bot.polling()
