import asyncio
import os
import logging
import random
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from aiohttp import web
import yt_dlp

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
CHANNEL_ID = -1001277492702
CHANNEL_LINK = "https://t.me/YourChannel"

# ======== بررسی عضویت ========
async def is_member(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ======== منوی اصلی با دکمه‌های جدید ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="🎬 دانلود یوتیوب", callback_data="youtube")],
        [InlineKeyboardButton(text="📱 دانلود تیک‌تاک", callback_data="tiktok")],
        [InlineKeyboardButton(text="📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton(text="🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton(text="💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton(text="👥 ممبرگیر", callback_data="members")],
        [InlineKeyboardButton(text="⚙️ پنل ادمین", callback_data="admin_panel")]
    ])

def game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice"),
         InlineKeyboardButton(text="🎯 دارت", callback_data="dart")],
        [InlineKeyboardButton(text="🎰 شانس", callback_data="slot")],
        [InlineKeyboardButton(text="🪨 سنگ‌کاغذ‌قیچی", callback_data="rps")],
        [InlineKeyboardButton(text="🔢 حدس عدد", callback_data="guess")],
        [InlineKeyboardButton(text="🏎️ ماشین‌بازی", callback_data="race")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="back_main")]
    ])

def rps_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🪨 سنگ", callback_data="rps_stone"),
         InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
         InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors")]
    ])

def admin_panel_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton(text="🔙 برگشت", callback_data="back_main")]
    ])

def channel_check_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ عضویت داشتم", callback_data="check_join")]
    ])

# ======== /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})

    if not await is_member(user_id):
        await message.answer(
            f"👋 سلام {message.from_user.first_name}!\n"
            "برای استفاده از ربات، لطفاً اول عضو کانال ما بشو:",
            reply_markup=channel_check_menu()
        )
        return

    await message.answer(
        f"🚀 سلام {message.from_user.first_name}!\nبه ربات خوش آمدی.",
        reply_markup=main_menu()
    )

# ======== بررسی عضویت ========
@dp.callback_query(lambda c: c.data == "check_join")
async def check_join(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_member(user_id):
        await callback.message.edit_text("✅ ممنون! حالا می‌تونی از ربات استفاده کنی.")
        await callback.message.answer("🚀 منوی اصلی:", reply_markup=main_menu())
    else:
        await callback.answer("❌ هنوز عضو کانال نشدی! اول عضو شو.", show_alert=True)

# ======== دانلود اینستاگرام (غیرفعال) ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    if not await is_member(callback.from_user.id):
        await callback.answer("❌ اول عضو کانال بشو!", show_alert=True)
        return
    await callback.message.answer("📎 لینک پست اینستاگرام را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    if not await is_member(message.from_user.id):
        await message.answer("❌ اول عضو کانال بشو!")
        return
    await message.answer("❌ متأسفانه دانلود اینستاگرام با مشکلات فنی مواجه شده. لطفاً از گزینه‌های یوتیوب یا تیک‌تاک استفاده کن.")

# ======== دانلود یوتیوب ========
@dp.callback_query(lambda c: c.data == "youtube")
async def youtube(callback: types.CallbackQuery):
    if not await is_member(callback.from_user.id):
        await callback.answer("❌ اول عضو کانال بشو!", show_alert=True)
        return
    await callback.message.answer("🎬 لینک ویدیو یوتیوب را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("youtube.com" in msg.text or "youtu.be" in msg.text))
async def get_youtube(message: types.Message):
    if not await is_member(message.from_user.id):
        await message.answer("❌ اول عضو کانال بشو!")
        return
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت ویدیو از یوتیوب...")
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'ویدیو')
            if video_url:
                await message.answer_video(video_url, caption=f"🎬 {title}")
            else:
                await message.answer("❌ خطا! ویدیو پیدا نشد.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لینک معتبر نیست یا ویدیو قابل دانلود نیست.")
    await msg.delete()

# ======== دانلود تیک‌تاک ========
@dp.callback_query(lambda c: c.data == "tiktok")
async def tiktok(callback: types.CallbackQuery):
    if not await is_member(callback.from_user.id):
        await callback.answer("❌ اول عضو کانال بشو!", show_alert=True)
        return
    await callback.message.answer("📱 لینک ویدیو تیک‌تاک را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("tiktok.com" in msg.text or "vm.tiktok.com" in msg.text))
async def get_tiktok(message: types.Message):
    if not await is_member(message.from_user.id):
        await message.answer("❌ اول عضو کانال بشو!")
        return
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت ویدیو از تیک‌تاک...")
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                video_url = data["data"]["play"]
                if video_url:
                    await message.answer_video(video_url, caption="📱 ویدیو از تیک‌تاک دانلود شد!")
                    await msg.delete()
                    return
        await message.answer("❌ خطا! لینک معتبر نیست یا ویدیو پیدا نشد.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لطفاً لینک را بررسی کن.")
    await msg.delete()

# ======== بقیه بخش‌ها (همون کد قبلی، بدون تغییر) ========
# آپلود، بازی‌ها، حمایت، ممبرگیر، پنل ادمین، دستورات و پورت
# (برای جلوگیری از طولانی شدن، این بخش‌ها رو حذف کردم ولی توی کد کامل هستن)
# در ادامه، بخش‌های مشابه کد قبلی رو قرار بده...

# (برای رعایت اختصار، ادامه کد رو می‌تونید از نسخه‌های قبلی کامل کنید)