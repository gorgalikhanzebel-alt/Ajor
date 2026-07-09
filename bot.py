import asyncio
import os
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from aiohttp import web
import instaloader

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

ADMIN_ID = 466050034

# ======== اطلاعات مستقیم اینستاگرام (فقط برای تست) ========
INSTA_USERNAME = "pishkhan72241148"
INSTA_PASSWORD = "Zz@123456"

# ======== راه‌اندازی نشست اینستاگرام ========
def get_instaloader_session():
    L = instaloader.Instaloader(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    try:
        L.load_session_from_file(INSTA_USERNAME)
        logging.info("✅ نشست اینستاگرام از فایل بارگذاری شد.")
    except:
        try:
            L.login(INSTA_USERNAME, INSTA_PASSWORD)
            L.save_session_to_file()
            logging.info("✅ لاگین به اینستاگرام موفق بود.")
        except Exception as e:
            logging.error(f"❌ لاگین ناموفق: {e}")
            return None
    return L

L = get_instaloader_session()

# ======== منوهای شیشه‌ای ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="🎮 بازی", callback_data="game")],
        [InlineKeyboardButton(text="⚙️ پنل ادمین", callback_data="admin_panel")]
    ])

def game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice"),
         InlineKeyboardButton(text="🎯 دارت", callback_data="dart")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="back_main")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="back_main")]
    ])

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(
        f"🚀 سلام {message.from_user.first_name}!\n"
        "به ربات خوش آمدی.\n"
        "از دکمه‌ها استفاده کن:",
        reply_markup=main_menu()
    )

# ======== دانلود اینستاگرام با یوزربات ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام رو بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت از اینستاگرام (با یوزربات)...")

    if L is None:
        await message.answer("❌ ربات به اینستاگرام متصل نیست! با ادمین تماس بگیرید.")
        await msg.delete()
        return

    try:
        post = instaloader.Post.from_url(L.context, url)
        if post is None:
            await message.answer("❌ پست پیدا نشد. لینک را بررسی کن.")
            await msg.delete()
            return

        if post.is_video:
            video_url = post.video_url
            await message.answer_video(video_url, caption="✅ ویدیو با موفقیت دانلود شد!")
        elif post.typename == "GraphImage":
            image_url = post.url
            await message.answer_photo(image_url, caption="✅ عکس با موفقیت دانلود شد!")
        else:
            await message.answer("❌ این پست چندرسانه‌ای است و فعلاً پشتیبانی نمی‌شود.")
    except Exception as e:
        logging.error(f"Instagram error: {e}")
        await message.answer("❌ خطا! لینک معتبر نیست یا اینستاگرام محدودیت ایجاد کرده است.")
    
    await msg.delete()

# ======== بازی‌ها ========
@dp.callback_query(lambda c: c.data == "game")
async def game(callback: types.CallbackQuery):
    await callback.message.answer("🎮 بازی انتخاب کن:", reply_markup=game_menu())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dice")
async def dice(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎲")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dart")
async def dart(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎯")
    await callback.answer()

# ======== پنل ادمین ========
@dp.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    await callback.message.answer("⚙️ پنل ادمین:", reply_markup=admin_menu())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stats")
async def stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    count = users_col.count_documents({})
    await callback.message.answer(f"📊 تعداد کاربران: {count}")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.answer("🔙 منوی اصلی:", reply_markup=main_menu())
    await callback.answer()

# ======== دستورات ========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("📖 راهنما:\n/start - شروع\n/help - راهنما\n/profile - آیدی من")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    await message.answer(f"👤 نام: {message.from_user.full_name}\n🆔 آیدی: {message.from_user.id}")

@dp.message()
async def unknown(message: types.Message):
    await message.answer("❌ دستور نامعتبر!\nاز /start استفاده کن.")

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