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

if not TOKEN or not MONGO_URI:
    logging.error("❌ متغیرهای محیطی تنظیم نشده‌اند!")
    exit(1)

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

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(
        f"سلام {message.from_user.first_name}! به ربات خوش آمدی 🚀",
        reply_markup=main_menu()
    )

# ======== دانلود اینستاگرام ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام رو بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    await message.answer("⏳ در حال دریافت از اینستاگرام...")
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, url)
        if post.is_video:
            await message.answer_video(post.video_url, caption="✅ دانلود شد!")
        else:
            await message.answer_photo(post.url, caption="✅ دانلود شد!")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لینک معتبر نیست یا پست خصوصی است.")

# ======== آپلود فیلم/عکس ========
@dp.callback_query(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("📤 لطفاً فیلم یا عکس خود را ارسال کن:")
    await callback.answer()

@dp.message(lambda msg: msg.photo or msg.video)
async def handle_media(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"✅ عکس شما با آیدی {file_id} دریافت شد!")
    elif message.video:
        file_id = message.video.file_id
        await message.answer(f"✅ فیلم شما با آیدی {file_id} دریافت شد!")

# ======== بازی ========
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

# ======== حمایت مالی ========
@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    await callback.message.answer("💳 لینک حمایت مالی: https://example.com")
    await callback.answer()

# ======== ممبرگیر ========
@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer("👥 برای دریافت لینک دعوت، به ادمین پیام بده: @Admin")
    await callback.answer()

# ======== پیام‌های دیگر ========
@dp.message()
async def unknown(message: types.Message):
    await message.answer("❌ دستور نامعتبر! از /start استفاده کن یا دکمه‌ها رو بزن.")

# ======== پورت برای رندر ========
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

# ======== اجرای اصلی ========
async def main():
    await start_web()
    logging.info("🤖 Starting bot polling...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())