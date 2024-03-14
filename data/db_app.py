import asyncio
import json
import traceback
import aiosqlite
from datetime import datetime, timedelta
from app.update_keys import update_days_keys, update_one_keys, update_expired_keys
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
                request INTEGER DEFAULT 0,
                request_img INTEGER DEFAULT 0,
                period_sub INTEGER DEFAULT 0,
                sub_date DATETIME,
                sub_date_end DATETIME,
                remaining_days INTEGER DEFAULT 0,
                referrer TEXT,
                referrals INTEGER DEFAULT 0,
                last_amount INTEGER DEFAULT 0,
                sum_amount INTEGER DEFAULT 0,
                balans INTEGER DEFAULT 0,
                banking_details TEXT DEFAULT ''
            )
        ''')
        await db.commit()


# Создание таблицы в базе данных
async def create_info_key_table():
    async with aiosqlite.connect('Api_keys.db') as db:
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


# Действие тарифов
async def update_tariffs_sub():
    # Подключаемся к базе данных
    async with aiosqlite.connect('Users.db') as connection:
        cursor = await connection.cursor()

        # Получаем текущую дату
        current_date = datetime.now()

        print('Сегодня: ', current_date)

        # Выполняем запрос для выборки данных
        await cursor.execute('SELECT user_id, sub_date, sub_date_end FROM users WHERE flag > 1')

        rows = await cursor.fetchall()
        print('Были извлечены данные для проверки срока действия тарифов:\n', rows)
        print("=============================================Проверяю базу=============================================")

        for row in rows:
            user_id, sub_date, sub_date_end = row

            # Проверяем, что значение sub_date не является None перед преобразованием
            if sub_date:
                # Преобразовываем sub_date_end в объект datetime
                sub_date_end_datetime = datetime.strptime(sub_date_end, "%d.%m.%Y")

                # Рассчитываем разницу в днях
                difference = await calculate_remaining_days(sub_date_end)
                # Обновляем остаток дней в БД
                await cursor.execute('''
                                        UPDATE users
                                        SET remaining_days = ?
                                        WHERE user_id = ?
                                        ''', (difference, user_id))

                # Вычитаем 3 дня из sub_date_end
                date_for_message = sub_date_end_datetime - timedelta(days=3)

                # Проверяем условия для обновления
                if current_date >= sub_date_end_datetime:
                    await cursor.execute('''UPDATE users 
                                            SET flag = 1, sub_date = ?, sub_date_end = ?, request = 15, request_img = 5 
                                            WHERE user_id = ?''',
                                         ('', '', user_id))
                    await bot.send_message(chat_id=user_id,
                                           text=f'У вас истек срок действия тарифа')
                elif current_date >= date_for_message:
                    await bot.send_message(chat_id=user_id,
                                           text=f'Действие вашего тарифа заканчивается {sub_date_end} 😱')

        # Сохраняем изменения и закрываем соединение
        await connection.commit()
    print("!!!!!!!!!!!!!!!!!!  Действие тарифов проверено  !!!!!!!!!!!!!!!!!!")


# Суточные лимиты
async def update_requests_db():
    # Подключаемся к базе данных
    async with aiosqlite.connect('Users.db') as connection:
        cursor = await connection.cursor()

        await cursor.execute('SELECT user_id , request_img, request FROM users WHERE flag == 1')
        rows = await cursor.fetchall()
        print('Были извлечены данные для проверки суточного лимита:\n', rows)

        print("///////////////////////////////  Проверяю базу  ///////////////////////////////")
        for row in rows:
            user_id, request_img, request = row
            if request < 15:
                await cursor.execute('UPDATE users SET request = ? WHERE user_id = ?', (15, user_id))
            if request_img < 5:
                await cursor.execute('UPDATE users SET request_img = ? WHERE user_id = ?', (5, user_id))

        # Сохраняем изменения и закрываем соединение
        await connection.commit()
    print("!!!!!!!!!!!!!!!!!!  Суточные лимиты обновлены  !!!!!!!!!!!!!!!!!!")


async def update_balans(value, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users
                                SET balans = ?
                                WHERE user_id = ?
                            ''', (value, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error update_balans: {e}")


async def sum_balans():
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('SELECT balans FROM users WHERE balans > 0')
            rows = await cursor.fetchall()
            sum_row = 0
            for row in rows:
                sum_row += row[0]
            return sum_row
    except Exception as e:
        print(f"Error sum_balans: {e}")


async def calculate_remaining_days(sub_date_end):
    try:
        sub_date_end = datetime.strptime(sub_date_end, '%d.%m.%Y')
        current_date = datetime.now()

        # Рассчитываем разницу в днях
        difference = sub_date_end - current_date

        # Получаем количество дней в разнице
        return difference.days
    except ValueError as e:
        print(f"Ошибка при преобразовании даты: {e}")
        return None


async def scheduler_keys():
    while True:
        await update_expired_keys()
        await update_one_keys()
        await asyncio.sleep(60)


async def scheduler():
    while True:
        current_time = datetime.now().strftime('%H:%M')
        if current_time == '04:00':
            await update_days_keys()
            await update_tariffs_sub()
            await asyncio.sleep(30)
            await update_requests_db()
            await asyncio.sleep(82800)
        else:
            await asyncio.sleep(30)


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


async def get_balans(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT balans
                                        FROM users
                                        WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Ошибка get_state_ai: {e}")
        return None


async def get_user(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT id
                                        FROM users
                                        WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result
    except Exception as e:
        print(f"Ошибка get_user: {e}")
        return None


# Добавление нового пользователя в базу данных
async def reg_user(user_id, registration_date, request, request_img, flag):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users 
                                SET registration_date = ?, 
                                request = ?, request_img = ?, flag = ?
                                WHERE user_id = ?
                            ''', (registration_date, request, request_img, flag, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error reg user: {e}")


async def add_user(user_id, username, referrer, ref):
    try:
        async with aiosqlite.connect('Users.db') as db:
            if ref:
                cursor = await db.execute('''
                                             SELECT user_id FROM users WHERE user_id = ?
                                          ''', (user_id,))
                check_user = await cursor.fetchone()

                if check_user is None:
                    await db.execute('''
                        UPDATE users
                        SET referrals = referrals + 1
                        WHERE user_id = ?
                    ''', (referrer,))
                    await db.execute('''
                                        INSERT INTO users (user_id, username, referrer)
                                        VALUES (?, ?, ?)
                                    ''', (user_id, username, referrer))
                    await db.commit()
            else:
                await db.execute('''
                                    INSERT INTO users (user_id, username, referrer)
                                    VALUES (?, ?, ?)
                                ''', (user_id, username, referrer))
                await db.commit()
    except Exception as e:
        print(f"Error add user: {e}")


# Обновление данных пользователя в базе данных
async def update_subscribe(flag, sub_date, sub_date_end, request, request_img, period, last_amount, user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('SELECT referrer, last_amount FROM users WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
            referrer, l_amount = result

            if referrer != 0 and l_amount == 0:
                await db.execute('''
                                    UPDATE users
                                    SET balans = balans + (? * 0.1)
                                    WHERE user_id = ?
                                ''', (last_amount, referrer))
                await db.commit()

            await db.execute('''
                                UPDATE users
                                SET flag = ?,
                                sub_date = ?,
                                sub_date_end = ?,
                                request = ?, 
                                request_img = ?,
                                period_sub = ?,
                                last_amount = ?,
                                sum_amount = sum_amount + ?
                                WHERE user_id = ?
                            ''', (flag, sub_date, sub_date_end, request, request_img, period,
                                  last_amount, last_amount, user_id))
            await db.commit()

            # Рассчитываем разницу в днях
            difference = await calculate_remaining_days(sub_date_end)
            # Обновляем остаток дней в БД
            await db.execute('''
                                                    UPDATE users
                                                    SET remaining_days = ?
                                                    WHERE user_id = ?
                                                    ''', (difference, user_id))
            await db.commit()
    except Exception as e:
        print(f"Error update_subscribe: {e}")


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


async def get_flag(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT flag FROM users WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result[0]
    except Exception as e:
        print(f"Получить флаг из БД не получилось: {e}")
        return None


async def get_req(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT request, request_img FROM users WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result
    except Exception as e:
        print(f"Получить реквесты из БД не получилось: {e}")
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


async def get_reqisists(user_id):
    try:
        async with aiosqlite.connect('Users.db') as db:
            cursor = await db.execute('''
                                        SELECT banking_details
                                        FROM users
                                        WHERE user_id = ?
                                        ''', (user_id,))
            result = await cursor.fetchone()
            return result[0]
    except Exception as e:
        print(f"Ошибка calculate_remaining_tokens: {e}")
        return None


async def save_banking_details(user_id, text):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''
                                UPDATE users
                                SET banking_details = ?
                                WHERE user_id = ?
                                ''', (text, user_id))  # Обнуляем историю чата
            await db.commit()
    except Exception as e:
        print(f"Ошибка при обнулении чата: {e}")
