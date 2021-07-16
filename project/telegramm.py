import uuid

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from telebot import TeleBot, types
from config import TOKEN
from datetime import datetime
from models import (my_apply, db, Departments, Employees, Dictionary, Dictionary_type, Log, Telegram_logs,
                    Telegram_users, Application, Sessions, check_dep_name, check_dep_id, get_dep_list, create_log,
                    check_emp_id, check_emp, get_emp_list, get_dictionary_value_list, get_app_list)

DB_URL = "sqlite:///crm.db"
my_apply = Flask("ITEA_PROJECT")

my_apply.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(my_apply)

bot = TeleBot(TOKEN)


# При авторизации у человека появится кнопка "Авторизация", при нажатии которой ему будет предложено поделиться номером телефона
def autorization(p_user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton('Авторизация', request_contact=True)])
    bot.send_message(p_user_id, """ Для продолжения нужна авторизация """, parse_mode="HTML", reply_markup=keyboard)

# Регистрация пользователя. Автоматически происходит подпись пользователя на рассылку новостей и прочего
def registration(p_chat_id, p_nickname, p_phone):
    dt = datetime.now()
    user_cr = Telegram_users(full_name="New", dt_add = dt, chat_id = p_chat_id, nickname=p_nickname,
                             password="12345678", role=1, phone=p_phone, is_subsсribed=1)
    db.session.add(user_cr)
    db.session.flush()
    db.session.commit()

# Когда человек заходит в бот и пишет /start (нажимает кнопку), переходим к авторизации
@bot.message_handler(commands=['start'])
def start(m):
    autorization(m.chat.id)

# Проверка пользователя на наличие в БД по номеру телефону
def check_customer_phone(p_phone):
    # запрос в БД
    sql_dep = db.select(Telegram_users.id).where(Telegram_users.phone == f'{p_phone}')
    # выполнение запроса
    res = db.session.execute(sql_dep).fetchone()
    return res

def check_customer_nickname(nickname):
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
    bot.send_message(p_user_id, """ Сделайте Ваш выбор: """, parse_mode="HTML", reply_markup=keyboard)

# Логика которая отрабатывает после передачи номера телефона пользователем
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
        if message.from_user.username is None:
            user = "Неизвестный"
        else:
            user = message.from_user.username
        phone = message.contact.phone_number
        res = check_customer_phone(phone)
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
    fio = message.text
    res = check_customer_nickname(message.from_user.username)
    user = Telegram_users.query.get(res[0])

    user.fio = fio
    db.session.commit()
    bot.send_message(message.from_user.id, f"Спасибо за регистрацию, {fio}. Добро пожаловать на наш сервис.")

    dt = datetime.now()
    telegram_log = Telegram_logs(created_dt = dt, nickname=fio, chat_id=message.from_user.id, customer_id=res[0], message="", type="Регистрация пользователя")
    db.session.add(telegram_log)
    db.session.flush()
    db.session.commit()

    menu_user(message.from_user.id)

# Меню типов заявки
def type_order(p_user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton('Проблема')])
    keyboard.add(*[types.KeyboardButton('Консультация')])
    bot.send_message(p_user_id, """ Сделайте Ваш выбор: """, parse_mode="HTML", reply_markup=keyboard)

# Регистрация проблемы
def reg_app_problem(message):
    res = check_customer_nickname(message.from_user.username)
    if res is None:
        bot.send_message(message.from_user.id, "Произошла ошибка, обратитесь к администратору.")
    else:
        msg_text = message.text
        bot.send_message(message.from_user.id, f"Мы зарегестрировали Вашу проблему: {msg_text}")

        dt = datetime.now()
        # creator_id - это ид пользователя, который создает заявку
        # executor_id = 1 это заявка автоматически падает на админа, потом будет распределение
        apply = Application(dt_add=dt, type="Проблема", description=msg_text, status="New",
                            code=str(uuid.uuid4()), creator_id=res[0], executor_id=1, dt_upd=dt)
        db.session.add(apply)
        db.session.flush()
        db.session.commit()

        dt = datetime.now()
        telegram_log = Telegram_logs(dt_add=dt, nickname=message.from_user.username, chat_id=message.from_user.id,
                                     customer_id=res[0], message=msg_text, type="Регистрация проблемы")
        db.session.add(telegram_log)
        db.session.flush()
        db.session.commit()

        menu_user(message.from_user.id)

# Регистрация запроса на консультацию
def reg_app_consult(message):

    res = check_customer_nickname(message.from_user.username)
    if res is None:
        bot.send_message(message.from_user.id, "Произошла ошибка, обратитесь к администратору.")
    else:
        msg_text = message.text
        bot.send_message(message.from_user.id, f"Мы зарегестрировали Ваш запрос на консультацию по вопросу: {msg_text}")

        dt = datetime.now()
        # creator_id - это ид пользователя, который создает заявку
        # executor_id = 1 это заявка автоматически падает на админа, потом будет распределение
        apply = Application(dt_add=dt, type="Консультация", description=msg_text, status="New",
                            code=str(uuid.uuid4()), creator_id=res[0], executor_id=1, dt_upd=dt)
        db.session.add(apply)
        db.session.flush()
        db.session.commit()

        dt = datetime.now()
        telegram_log = Telegram_logs(dt_add=dt, nickname=message.from_user.username, chat_id=message.from_user.id,
                                     message=msg_text, type="Регистрация заявки на консультацию")
        db.session.add(telegram_log)
        db.session.flush()
        db.session.commit()

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
    print(message.text)
    if message.text == "Создать заявку":
        print("Переходим к созданию заявки")

        msg = bot.reply_to(message, "Выберите тип заявки:")
        type_order(message.from_user.id)
        bot.register_next_step_handler(msg, reg_app)


    elif message.text == "Созданные Вами заявки":

            res = check_customer_nickname(message.from_user.username)
            sql = db.select(Application.id, Application.dt_add, Application.status, Application.executor_id).where(Application.creator_id == f'{res[0]}')
            res = db.session.execute(sql).fetchall()
            for i in res:
                if i[3] == 1 or i[3] is None:
                    executor = 'Не назначен'
                else:
                    executor = i[3]
                res_text = f"""
<b>Номер заявки в системе:</b> {i[0]}
<b>Дата создания:</b> {i[1]}
<b>Статус:</b> {i[2]}
<b>Ответственный:</b> {executor}
                """
                bot.send_message(message.from_user.id, res_text, parse_mode="HTML")

    else:
        nick = message.from_user.username
        res = check_customer_nickname(nick)
        if res is None:
            res_text = f"Неизвестная команда: {message.text} от незарегестрированного пользователя: {message.from_user.username} с id: {message.from_user.id}"
            dt = datetime.now()

            telegram_log = Telegram_logs(dt_add=dt, nickname=nick, chat_id=message.from_user.id,
                                         message=message.text, type="Получено сообщение")
            db.session.add(telegram_log)
            db.session.flush()
            db.session.commit()
        else:
            bot.send_message(message.from_user.id, "Неизвестная команда")
            dt = datetime.now()
            telegram_log = Telegram_logs(dt_add=dt, nickname=nick, chat_id=message.from_user.id,
                                         message=message.text, type="Получено сообщение")
            db.session.add(telegram_log)
            db.session.flush()
            db.session.commit()


if __name__ == "__main__":
    bot.polling()

