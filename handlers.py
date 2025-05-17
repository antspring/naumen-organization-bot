from aiogram import Router

router = Router(name=__name__)

@router.message()
async def message_handler(message):
    await message.answer('Hello')