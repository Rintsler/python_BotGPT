import asyncio
import logging
import sys
from data.config import dp, bot
from data.db_app import create_info_key_table, create_table
from nav.handlers import *


async def main():
    await create_info_key_table()
    await create_table()

    dp.include_router(router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        # Создаем и запускаем asyncio loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
