import asyncio
import json
import traceback
import aiosqlite
from datetime import datetime

from data.config import bot


async def create_table():
    async with aiosqlite.connect('Users.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_ai TEXT,
                user_id INTEGER,
                flag INTEGER,
                username TEXT,
                registration_date DATETIME,
                chat_history TEXT NULL DEFAULT '[]',
                response_history TEXT NULL DEFAULT '[]',
                request INTEGER,
                request_img INTEGER,
                period_sub INTEGER,
                sub_date DATETIME,
                remaining_days INTEGER
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


async def update_tariffs_sub():
    # Подключаемся к базе данных
    async with aiosqlite.connect('Users.db') as connection:
        cursor = await connection.cursor()

        # Получаем текущую дату
        current_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')

        # Выполняем запрос для выборки данных
        await cursor.execute('SELECT user_id, period_sub, sub_date FROM users WHERE flag > 2')

        rows = await cursor.fetchall()
        print(rows)

        print("Проверяю базу")
        for row in rows:
            user_id, period_sub, sub_date = row
            # Проверяем, что значение sub_date не является None перед преобразованием
            if sub_date:
                sub_date = datetime.strptime(sub_date, '%Y-%m-%d %H:%M')
                # Увеличить sub_date на один месяц
                sub_date_month = sub_date.replace(month=(sub_date.month + 1) % 12 + 1)
                date_send_m_month = sub_date_month.replace(day=sub_date_month.day - 4)

                sub_date_month = datetime.strftime(sub_date_month, '%Y-%m-%d')
                date_send_m_month = datetime.strftime(date_send_m_month, '%Y-%m-%d')

                # Увеличить sub_date на пол года
                if sub_date.month + 6 <= 12:
                    sub_date_6m = sub_date.replace(month=sub_date.month + 6)
                else:
                    sub_date_6m = sub_date.replace(year=sub_date.year + 1, month=(sub_date.month + 6) % 12,
                                                   day=sub_date.day)
                date_send_m_6m = sub_date_6m.replace(day=sub_date_6m.day - 4)

                sub_date_6m = datetime.strftime(sub_date_6m, '%Y-%m-%d')
                date_send_m_6m = datetime.strftime(date_send_m_6m, '%Y-%m-%d')

                # Увеличить sub_date на один год
                sub_date_year = sub_date.replace(year=sub_date.year + 1)
                date_send_m_year = sub_date_year.replace(day=sub_date_year.day - 4)

                sub_date_year = datetime.strftime(sub_date_year, '%Y-%m-%d')
                date_send_m_year = datetime.strftime(date_send_m_year, '%Y-%m-%d')

                # Проверяем условия для обновления
                if period_sub == 1:
                    if current_date >= sub_date_month:
                        await cursor.execute('UPDATE users SET flag = 2, sub_date = ? WHERE user_id = ?',
                                             ('', user_id))
                    elif current_date > date_send_m_month:
                        await bot.send_message(chat_id=user_id,
                                               text=f'Действие вашего тарифа заканчивается {sub_date_month} 😱')
                elif period_sub == 6:
                    print("дата", sub_date_6m)
                    if current_date >= sub_date_6m:
                        await cursor.execute('UPDATE users SET flag = 2, sub_date = ? WHERE user_id = ?',
                                             ('', user_id))
                    elif current_date > date_send_m_6m:
                        await bot.send_message(chat_id=user_id,
                                               text=f'Действие вашего тарифа заканчивается {sub_date_6m} 😱')
                elif period_sub == 12:
                    print(period_sub)
                    print(current_date, '==', sub_date_year)
                    if current_date >= sub_date_year:
                        await cursor.execute('UPDATE users SET flag = 2, sub_date = ? WHERE user_id = ?',
                                             ('', user_id))
                    elif current_date > date_send_m_year:
                        await bot.send_message(chat_id=user_id,
                                               text=f'Действие вашего тарифа заканчивается {sub_date_year} 😱')

        # Сохраняем изменения и закрываем соединение
        await connection.commit()
    print("Обновил подписки")


async def update_requests_db():
    # Подключаемся к базе данных
    async with aiosqlite.connect('Users.db') as connection:
        cursor = await connection.cursor()

        await cursor.execute('SELECT user_id , request_img, request FROM users WHERE flag == 1')
        rows = await cursor.fetchall()

        print("Проверяю базу")
        for row in rows:
            user_id, request_img, request = row
            if request < 15:
                await cursor.execute('UPDATE users SET request = ? WHERE user_id = ?', (15, user_id))
            if request_img < 5:
                await cursor.execute('UPDATE users SET request_img = ? WHERE user_id = ?', (5, user_id))

        # Сохраняем изменения и закрываем соединение
        await connection.commit()
    print("Обновил лимиты")


async def scheduler():
    while True:
        await update_tariffs_sub()
        await update_requests_db()
        await asyncio.sleep(86400)


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


# Обновление флага после потраченных 30/10
async def update_flag_requests_img(user_id, flag):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users 
                                SET user_id = ?, flag = ?
                                WHERE user_id = ?
                            ''', (user_id, flag, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error reg user: {e}")


# Обновление флага после потраченных 30/10
async def update_flag_requests(user_id, flag):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users 
                                SET user_id = ?, flag = ?
                                WHERE user_id = ?
                            ''', (user_id, flag, user_id))
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
            result = await cursor.fetchone()
            return result
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
