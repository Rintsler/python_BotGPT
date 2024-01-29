import asyncio
from datetime import datetime, timedelta
import aiosqlite


async def update_expired_keys():
    try:
        async with aiosqlite.connect('Users.db') as db:
            async with db.execute(
                    '''SELECT * 
                    FROM info_key 
                    WHERE status_key=2 
                    AND (julianday("now") - julianday(status_change)) * 24 * 60 > 1'''
            ) as cursor:
                expired_keys = await cursor.fetchall()

                for key in expired_keys:
                    await db.execute('''UPDATE info_key SET status_key=0 WHERE api_key=?''', (key[1],))
                    print(f"Key {key[1]} status updated to 0")
                await db.commit()
    except Exception as e:
        print(f"Error updating expired keys: {e}")


async def update_days_keys():
    try:
        async with aiosqlite.connect('Users.db') as db:
            async with db.execute(
                    '''SELECT * 
                    FROM info_key 
                    WHERE status_key=3 
                    AND (julianday("now") - julianday(status_change)) * 24 > 24'''
            ) as cursor:
                expired_keys = await cursor.fetchall()

                for key in expired_keys:
                    await db.execute('''UPDATE info_key SET status_key=0, requests_day_key = 0 WHERE api_key=?''',
                                     (key[1],))
                    print(f"Key {key[1]} status updated to 0")
                await db.commit()
    except Exception as e:
        print(f"Error updating days keys: {e}")


async def update_one_keys():
    try:
        async with aiosqlite.connect('Users.db') as db:
            three_minutes_ago = datetime.now() - timedelta(minutes=3)
            async with db.execute(
                    '''SELECT * FROM info_key WHERE status_key=1 AND status_change < ?''', (three_minutes_ago,)
            ) as cursor:
                expir_keys = await cursor.fetchall()

                for key in expir_keys:
                    await db.execute('''UPDATE info_key SET status_key=0 WHERE api_key=?''', (key[1],))
                    print(f"Key {key[1]} status updated to 0")
                await db.commit()
    except Exception as e:
        print(f"Error updating one keys: {e}")


async def schedule_thread():
    while True:
        await asyncio.gather(
            update_expired_keys(),
            update_days_keys(),
            update_one_keys()
        )
        await asyncio.sleep(1)


async def get_unused_key():
    try:
        async with aiosqlite.connect('Users.db') as db:
            async with db.execute('''
                                    SELECT * 
                                    FROM info_key 
                                    WHERE status_key=0 
                                    AND where_use="chat" LIMIT 1
                                    ''') as cursor:
                unused_key_info = await cursor.fetchone()

                if unused_key_info:
                    if unused_key_info[5] == 200:
                        await db.execute(
                            '''UPDATE info_key SET status_key=3, status_change=datetime("now") WHERE api_key=?''',
                            (unused_key_info[1],))
                        await db.commit()
                    else:
                        return unused_key_info[1]  # Возвращаем API ключ
                print("Нет доступных ключей или запросов недостаточно, ожидание...")
                await asyncio.sleep(10)
    except Exception as e:
        print(f"Error getting unused key: {e}")


async def log_error(api_key, error_text):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''UPDATE info_key SET status_error=? WHERE api_key=?''', (error_text, api_key))
            await db.commit()
    except Exception as e:
        print(f"Error logging error: {e}")


async def update_key_status(api_key, status):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''UPDATE info_key SET status_key=?, status_change=datetime("now") WHERE api_key=?''',
                             (status, api_key))
            await db.execute(
                '''UPDATE info_key SET requests_day_key = COALESCE(requests_day_key, 0) + 1 WHERE api_key=?''',
                (api_key,))
            await db.commit()
    except Exception as e:
        print(f"Error updating key status: {e}")


async def reset_key_status(api_key):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''UPDATE info_key SET status_key=0,status_change=datetime("now") WHERE api_key=?''',
                             (api_key,))
            await db.commit()
    except Exception as e:
        print(f"Error resetting key status: {e}")


async def set_key_status_to_2(api_key):
    try:
        async with aiosqlite.connect('Users.db') as db:
            await db.execute('''UPDATE info_key SET status_key=2 WHERE api_key=?''', (api_key,))
            await db.commit()
    except Exception as e:
        print(f"Error setting key status to 2: {e}")
