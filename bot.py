import asyncio
import os
import logging
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
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

# ======== منوی اصلی (دکمه‌های شیشه‌ای) ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton(text="🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton(text="💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton(text="👥 ممبرگیر", callback_data="members")]
    ])

# ======== منوی دوم برای بازی ========
def game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice")],
        [InlineKeyboardButton(text="🎯 دارت", callback_data="dart")]
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

# ======== دانلود اینستاگرام با روش جدید ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    await message.answer("⏳ در حال دریافت از اینستاگرام...")

    try:
        # استفاده از API رایگان (بدون نیاز به لاگین)
        api_url = f"https://api.instagram.com/oembed?url={url}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            thumbnail_url = data.get("thumbnail_url")
            if thumbnail_url:
                await message.answer_photo(thumbnail_url, caption="✅ عکس از اینستاگرام دریافت شد!")
                return
        
        # روش جایگزین: استفاده از سرویس viddownload (رایگان)
        download_api = f"https://viddownload.in/api/instagram?url={url}"
        response = requests.get(download_api)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("media"):
                media_url = data["media"]
                if data.get("type") == "video":
                    await message.answer_video(media_url, caption="✅ ویدیو دانلود شد!")
                else:
                    await message.answer_photo(media_url, caption="✅ عکس دانلود شد!")
                return
        
        # اگر هیچ‌کدام کار نکرد
        await message.answer("❌ خطا! لینک معتبر نیست یا اینستاگرام محدودیت ایجاد کرده.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لطفاً لینک را بررسی کن یا بعداً امتحان کن.")

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
    await callback.message.answer("یک بازی انتخاب کن:", reply_markup=game_menu())
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

# ======== دستورات جدید (از عکس شما) ========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("📖 راهنما:\n/start - شروع\n/help - راهنما\n/about - درباره ربات\n/ping - بررسی وضعیت\n/time - ساعت و تاریخ\n/profile - آیدی من\n/stat - آمار ربات\n/joke - جوک تصادفی\n/quote - نقل قول انگیزشی")

@dp.message(Command("about"))
async def about(message: types.Message):
    await message.answer("🤖 این یک ربات قدرتمند است!\nساخته شده با aiogram و عشق ❤️")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("✅ ربات آنلاین است!")

@dp.message(Command("time"))
async def time_command(message: types.Message):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(f"🕒 زمان فعلی: {now}")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    user = message.from_user
    await message.answer(f"👤 نام: {user.full_name}\n🆔 آیدی: {user.id}")

@dp.message(Command("stat"))
async def stat(message: types.Message):
    count = users_col.count_documents({})
    await message.answer(f"📊 تعداد کاربران: {count}")

@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا مرغ از جاده رد شد؟ برای اینکه به اون طرف برسه! 😂", "بهترین زبان برنامه‌نویسی؟ پایتون! 🐍", "ربات خوب، رباتی که جواب بده!"]
    import random
    await message.answer(random.choice(jokes))

@dp.message(Command("quote"))
async def quote(message: types.Message):
    quotes = ["همیشه به فکر فردا باش!", "موفقیت یعنی بلند شدن دوباره!", "کد بزن و لذت ببر!"]
    import random
    await message.answer(f"💬 {random.choice(quotes)}")

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