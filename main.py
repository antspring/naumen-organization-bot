import asyncio
import os
import argparse
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web
from handlers import router


load_dotenv()
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(router)

async def start_polling():
    await dp.start_polling(bot)

async def start_webhook():
    app = web.Application()
    dp.shutdown.register(bot.delete_webhook)

    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_request_handler.register(app, path=os.getenv('WEBHOOK_PATH'))
    setup_application(app, dp, bot=bot)

    await bot.set_webhook(os.getenv('WEBHOOK_URL'))
    web.run_app(app, host="0.0.0.0", port=8443)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--webhook', action="store_true")
    parser.add_argument('--seed', action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.webhook:
        asyncio.run(start_webhook())
    else:
        asyncio.run(start_polling())
