import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from aiohttp import web

# ======== تنظیمات ========
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not TOKEN or not MONGO_URI:
    logging.error("❌ متغیرهای محیطی تنظیم نشده‌اند!")
    exit(1)

# اتصال به دیتابیس
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_col = db["users"]

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ======== منوی اصلی ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton(text="🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton(text="💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton(text="👥 ممبرگیر", callback_data="members")]
    ])

# ======== دستورات ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(f"سلام {message.from_user.first_name}! ربات فعال است 🚀", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("لینک پست اینستاگرام را بفرست:")
    await callback.answer()

# بقیه کالبک‌ها به همین سادگی...
@dp.callback_query(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("فیلم یا عکس بفرست:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "game")
async def game(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice")],
        [InlineKeyboardButton(text="🎯 دارت", callback_data="dart")]
    ])
    await callback.message.answer("بازی انتخاب کن:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data in ["dice", "dart"])
async def play(callback: types.CallbackQuery):
    emoji = "🎲" if callback.data == "dice" else "🎯"
    await callback.message.answer_dice(emoji=emoji)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    await callback.message.answer("💳 لینک حمایت: https://example.com")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer("👥 برای لینک دعوت به ادمین پیام بده")
    await callback.answer()

@dp.message()
async def echo(message: types.Message):
    await message.answer("❌ دستور نامعتبر! از /start استفاده کن.")

# ======== راه‌اندازی پورت برای رندر ========
async def health_check(request):
    return web.Response(text="✅ Bot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"✅ Web server started on port {port}")

# ======== اجرا ========
async def main():
    # پورت رو باز کن
    await start_web()
    # شروع ربات
    logging.info("🤖 Starting bot polling...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())