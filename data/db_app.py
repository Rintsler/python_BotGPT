import json
import traceback
import aiosqlite


async def create_table():
    async with aiosqlite.connect('Users.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_ai TEXT,
                user_id INTEGER,
                flag INTEGER DEFAULT 0,
                username TEXT,
                registration_date DATETIME,
                chat_history TEXT NULL DEFAULT '[]',
                response_history TEXT NULL DEFAULT '[]',
                request INTEGER DEFAULT 0,
                request_img INTEGER DEFAULT 0,
                period_sub INTEGER DEFAULT 0,
                sub_date DATETIME,
                remaining_days INTEGER DEFAULT 0,
                remaining_tokens INTEGER DEFAULT 0
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


async def set_state_ai(user_id, state_ai):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users
                                SET state_ai = ?
                                WHERE user_id = ?
                            ''', (state_ai, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error updating state_ai: {e}")


async def get_state_ai(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT state_ai
                                        FROM users
                                        WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Ошибка get_state_ai: {e}")
        return None


# Добавление нового пользователя в базу данных
async def reg_user(user_id, username, registration_date, request, request_img, flag):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users 
                                SET user_id = ?, username = ?, registration_date = ?, 
                                request = ?, request_img = ?, flag = ?
                                WHERE user_id = ?
                            ''', (user_id, username, registration_date, request, request_img, flag, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error reg user: {e}")


async def add_user(user_id, username):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                INSERT INTO users (user_id, username)
                                VALUES (?, ?)
                            ''', (user_id, username))
            await db.commit()
    except Exception as e:
        print(f"Error add user: {e}")


# Обновление данных пользователя в базе данных
async def update_subscribe(flag, sub_date, request, request_img, period, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users
                                SET flag = ?,
                                sub_date = ?,
                                request = ?, 
                                request_img = ?,
                                period_sub = ?
                                WHERE user_id = ?
                            ''', (flag, sub_date, request, request_img, period, user_id))
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


async def get_flag_and_req(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT flag, request, request_img FROM users WHERE user_id = ?
                                        ''', (user_id,))
            flag = await cursor.fetchone()
            return flag
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
                            ''', (
                json.dumps(user_history, ensure_ascii=False), json.dumps(response_history, ensure_ascii=False),
                user_id))
            await db.commit()
    except Exception as e:
        print(f"Ошибка при обновлении истории чата: {e}")
        traceback.print_exc()
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


async def update_requests(user_id, request, request_img):
    try:
        async with aiosqlite.connect('Users.db') as db:
            request = request - 1
            request_img = request_img - 1
            await db.execute('''
                                UPDATE users
                                SET request = ?,
                                request_img = ?
                                WHERE user_id = ?
                                ''', (request, request_img, user_id))
            await db.commit()
    except Exception as e:
        print(f"Ошибка calculate_remaining_tokens: {e}")
        return None


async def get_user_data(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT *
                                        FROM users
                                        WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result
    except Exception as e:
        print(f"Ошибка calculate_remaining_tokens: {e}")
        return None
