import json
import aiosqlite
from sqlalchemy.ext.declarative import declarative_base
from data.bufer import B

u = B()


# Base = declarative_base()


# Создаем базу данных в памяти
# engine = create_engine('sqlite:///Users.db', echo=True)

# Создаем сессию
# session = Session(engine)


# class User(Base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer)
#     username = Column(String)
#     registration_date = Column(DateTime)
#     chat_history = Column(Text, nullable=False, default='[]')
#     response_history = Column(Text, nullable=False, default='[]')
#     tokens = Column(Integer, default=0)
#     tokens_used = Column(Integer, default=0)
#     subscribe = Column(Text, default='[]')
#     sub_date = Column(DateTime)
#     balance = Column(Integer, default=0)
#     remaining_tokens = Column(Integer, default=0)
#     flag = Column(Integer, default=0)
#
#
# class InfoKey(Base):
#     __tablename__ = 'info_key'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     api_key = Column(String, nullable=False)
#     status_key = Column(Integer)
#     status_limits = Column(Integer)
#     requests_key = Column(Integer)
#     requests_day_key = Column(Integer)
#     cost = Column(Integer)
#     where_use = Column(String)
#     status_change = Column(DateTime, server_default='CURRENT_TIMESTAMP')
#     status_error = Column(String)
#     login = Column(String)
#     password = Column(String)


async def create_table():
    async with aiosqlite.connect('Users.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                registration_date DATETIME,
                chat_history TEXT NULL DEFAULT '[]',
                response_history TEXT NULL DEFAULT '[]',
                tokens INTEGER DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                subscribe TEXT,
                sub_date DATETIME,
                balance INTEGER DEFAULT 0,
                remaining_tokens INTEGER DEFAULT 0,
                flag INTEGER DEFAULT 0
            )
        ''')
        await db.commit()


# Создание таблицы в базе данных
async def create_info_key_table():
    async with aiosqlite.connect('Users.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS info_key (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT NOT NULL,
                status_key INTEGER,
                status_limits INTEGER,
                requests_key INTEGER,
                requests_day_key INTEGER,
                cost INTEGER,
                where_use TEXT,
                status_change DATETIME DEFAULT CURRENT_TIMESTAMP,
                status_error TEXT,
                login TEXT,
                password TEXT
            )
        ''')
        await db.commit()


# Добавление нового пользователя в базу данных
async def add_user(user_id, username, tokens, flag):
    async with aiosqlite.connect('Users.db') as db:
        await db.execute('''
            INSERT INTO users (user_id, username, tokens, flag)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, tokens, flag))
        await db.commit()


# Обновление данных пользователя в базе данных
async def reg_user(reg_date, flag, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET registration_date = ?,
            flag = ?
            WHERE user_id = ?
        ''', (reg_date, flag, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error updating user: {e}")


# Обновление данных пользователя в базе данных
async def update_subscribe(subscribe, sub_date, tokens, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET subscribe = ?,
            sub_date = ?,
            tokens = ?
            WHERE user_id = ?
        ''', (subscribe, sub_date, tokens, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error updating user: {e}")


async def new_chat(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET chat_history = ?,
            response_history = ?
            WHERE user_id = ?
            ''', ('[]', '[]', user_id))  # Обнуляем историю чата
            await db.commit()
    except Exception as e:
        print(f"Ошибка при обнулении чата: {e}")


async def get_user(user_id):
    from data.controllers import user
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''SELECT username, registration_date, chat_history, response_history,
                                      tokens, tokens_used, subscribe, sub_date, balance, remaining_tokens, flag
                                      FROM users WHERE user_id = ?''', (user_id,))
            user_data = await cursor.fetchone()
            print('user_data: ', user_data)
            if user_data:
                # Распаковываем кортеж в переменные
                user.username, user.registration_date, user.chat_history, user.response_history, user.tokens, \
                    user.tokens_used, user.subscribe, user.sub_date, user.balance, user.remaining_tokens, \
                    user.flag = user_data

                print(f"Username: {user.username}\n"
                      f"registration_date: {user.registration_date}\n"
                      f"tokens: {user.tokens}\n"
                      f"tokens_used: {user.tokens_used}\n"
                      f"subscribe: {user.subscribe}\n"
                      f"sub_date: {user.sub_date}\n"
                      f"balance: {user.balance}\n"
                      f"remaining_tokens: {user.remaining_tokens}\n"
                      f"flag: {user.flag}\n")
            else:
                print("Данные пользователя пусты.")
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None


async def get_flag(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
            SELECT flag FROM users WHERE user_id = ?
            ''', (user_id,))
            flag = await cursor.fetchone()
            return flag[0]
    except Exception as e:
        print(f"Получить флаг из БД не получилось: {e}")
        return None


async def get_user_history(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
            SELECT chat_history, response_history FROM users WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            if result is not None:
                chat_history, response_history = result
                return chat_history, response_history
            else:
                return [], []
    except Exception as e:
        print(f"Ошибка при получении истории чата: {e}")
        return None


async def update_user_history(user_id, user_history, response_history):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET chat_history = ?,
                response_history = ?
            WHERE user_id = ?
        ''', (json.dumps(user_history, ensure_ascii=False),
              json.dumps(response_history, ensure_ascii=False),
              user_id))
        await db.commit()
    except Exception as e:
        print(f"Ошибка при обновлении истории чата: {e}")
        return None


async def add_response_to_history(user_id, response_history):
    # Обновляем историю ответов в базе данных
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET response_history = ?
            WHERE user_id = ?
            ''', (json.dumps(response_history, ensure_ascii=False), user_id))
            await db.commit()
    except Exception as e:
        print(f"Ошибка при обновлении истории ответов: {e}")
        return None


async def update_tokens_used(tokens_used, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
            UPDATE users
            SET tokens_used = tokens_used + ?
            WHERE user_id = ?
            ''', (tokens_used, user_id))
            await db.commit()
    except Exception as e:
        print(f"Ошибка при обновлении поля использованных токенов: {e}")
        return None


async def calculate_remaining_tokens(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
            SELECT tokens, tokens_used
            FROM users
            WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            if result:
                tokens, tokens_used = result
                remaining_tokens = tokens - tokens_used
                await db.execute('''
                            UPDATE users
                            SET remaining_tokens = ?
                            WHERE user_id = ?
                            ''', (remaining_tokens, user_id))
                await db.commit()
                return remaining_tokens
            else:
                return 0
    except Exception as e:
        print(f"Ошибка calculate_remaining_tokens: {e}")
        return None


async def get_subscribe(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
            SELECT subscribe
            FROM users
            WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            return result
    except Exception as e:
        print(f"Ошибка calculate_remaining_tokens: {e}")
        return None