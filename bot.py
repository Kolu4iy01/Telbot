import asyncio
from aiogram import Bot, Dispatcher

from routers.command_router import commands_router
from routers.admin_router import admin_router
from routers.white_list_router import white_list_router
from routers.request_router import request_router
from shared import API_TOKEN


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


dp.include_routers(commands_router, admin_router, white_list_router, request_router)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
