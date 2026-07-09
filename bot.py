import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import instaloader
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_col = db["users"]

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton(text="🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton(text="💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton(text="👥 ممبرگیر", callback_data="members")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(f"سلام {message.from_user.first_name}! به ربات خوش آمدی 🚀", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("لینک پست اینستاگرام را بفرست:")
    await callback.answer()

@dp.message(lambda msg: "instagram.com" in msg.text)
async def get_insta(message: types.Message):
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, message.text)
        if post.is_video:
            await message.answer_video(post.video_url, caption="📥 دانلود شد!")
        else:
            await message.answer_photo(post.url, caption="📥 دانلود شد!")
    except:
        await message.answer("❌ خطا! لینک معتبر نیست یا پست خصوصی است.")

@dp.callback_query(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("فیلم یا عکس خود را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.photo or msg.video)
async def save_media(message: types.Message):
    await message.answer("✅ فایل شما دریافت شد!")

@dp.callback_query(lambda c: c.data == "game")
async def game(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice")],
        [InlineKeyboardButton(text="🎯 دارت", callback_data="dart")]
    ])
    await callback.message.answer("یک بازی انتخاب کن:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dice")
async def dice(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎲")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dart")
async def dart(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎯")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    await callback.message.answer("💳 لینک حمایت مالی: https://example.com")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer("👥 برای دریافت لینک دعوت، به ادمین پیام بده: @Admin")
    await callback.answer()

@dp.message()
async def echo(message: types.Message):
    await message.answer("❌ دستور نامعتبر! از /start استفاده کن.")

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    logging.info("Web server started on port " + os.environ.get("PORT", "10000"))

async def main():
    asyncio.create_task(start_web())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())