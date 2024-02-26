import asyncio
import logging
import sys
from data.config import dp, admins_id
from data.db_app import create_info_key_table, create_table, scheduler
from nav.handlers import *


async def main():
    await create_info_key_table()
    await create_table()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        # Создаем и запускаем asyncio loop
        loop = asyncio.get_event_loop()

        # Запуск планировщика в том же цикле событий asyncio
        loop.create_task(scheduler())
        loop.run_until_complete(main())
        asyncio.run(main())


    except KeyboardInterrupt:
        print('Бот завершил работу')
