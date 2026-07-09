import asyncio
import os
import logging
import requests
from datetime import datetime
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

ADMIN_ID = 466050034

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

# ======== دانلود اینستاگرام (واقعی) ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام رو بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت از اینستاگرام...")

    try:
        # استفاده از API رایگان viddownload.in
        api_url = f"https://viddownload.in/api/instagram?url={url}"
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("media"):
                media_url = data["media"]
                if data.get("type") == "video":
                    await message.answer_video(media_url, caption="✅ ویدیو دانلود شد!")
                else:
                    await message.answer_photo(media_url, caption="✅ عکس دانلود شد!")
                await msg.delete()
                return

        # API جایگزین: apido.ir
        api_url2 = f"https://apido.ir/api/instagram/post?url={url}"
        response2 = requests.get(api_url2, timeout=15)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("status") == "success" and data2.get("data"):
                post = data2["data"]
                if post.get("type") == "video":
                    await message.answer_video(post["download_url"], caption="✅ ویدیو دانلود شد!")
                elif post.get("type") == "image":
                    await message.answer_photo(post["download_url"], caption="✅ عکس دانلود شد!")
                else:
                    await message.answer("❌ نوع پست پشتیبانی نمی‌شود.")
                await msg.delete()
                return

        # اگر هیچ API جواب نداد
        await message.answer("❌ خطا! لینک معتبر نیست یا اینستاگرام محدودیت ایجاد کرده.")

    except Exception as e:
        logging.error(f"Instagram error: {e}")
        await message.answer("❌ خطا! لطفاً لینک را بررسی کن یا بعداً امتحان کن.")

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