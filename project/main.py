from routes import *

# Очистка всех сессий (таблица crm.sessions)
db.session.query(Sessions).delete()
db.session.commit()


if __name__ == "__main__":
    my_apply.run(debug=True)
