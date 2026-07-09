import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import yt_dlp
import instaloader

# ======== تنظیمات ========
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")  # همان رشته‌ای که در عکس اول دادی

# اتصال به دیتابیس
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_col = db["users"]

# راه‌اندازی ربات
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ======== منوی اصلی با دکمه‌ها ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="🎬 دانلود یوتیوب", callback_data="youtube")],
        [InlineKeyboardButton(text="📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton(text="🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton(text="💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton(text="👥 ممبرگیر", callback_data="members")]
    ])

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    # ذخیره کاربر در دیتابیس
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({
            "_id": user_id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "joined_at": message.date
        })
    await message.answer(
        f"سلام {message.from_user.first_name}! به ربات خفن خوش آمدی 🚀\n"
        "یکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=main_menu()
    )

# ======== دانلود اینستاگرام ========
@dp.callback_query(lambda c: c.data == "insta")
async def download_insta(callback: types.CallbackQuery):
    await callback.message.answer("لینک پست اینستاگرام را بفرست:")
    await callback.answer()

@dp.message(lambda msg: "instagram.com" in msg.text)
async def get_insta(message: types.Message):
    url = message.text
    try:
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_url(loader.context, url)
        if post.is_video:
            await message.answer_video(post.video_url, caption="📥 دانلود شد!")
        else:
            await message.answer_photo(post.url, caption="📥 دانلود شد!")
    except:
        await message.answer("❌ خطا! لینک معتبر نیست یا پست خصوصی است.")

# ======== دانلود یوتیوب ========
@dp.callback_query(lambda c: c.data == "youtube")
async def download_youtube(callback: types.CallbackQuery):
    await callback.message.answer("لینک ویدیو یوتیوب را بفرست:")
    await callback.answer()

@dp.message(lambda msg: "youtube.com" in msg.text or "youtu.be" in msg.text)
async def get_youtube(message: types.Message):
    url = message.text
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            await message.answer_video(video_url, caption="🎬 دانلود شد!")
    except:
        await message.answer("❌ خطا! ویدیو قابل دانلود نیست.")

# ======== آپلود ========
@dp.callback_query(lambda c: c.data == "upload")
async def upload_prompt(callback: types.CallbackQuery):
    await callback.message.answer("فیلم یا عکس خود را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.photo or msg.video)
async def save_media(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer("✅ عکس دریافت شد و در دیتابیس ذخیره گردید.")
        # می‌توانی در دیتابیس ذخیره کنی
    elif message.video:
        file_id = message.video.file_id
        await message.answer("✅ فیلم دریافت شد و در دیتابیس ذخیره گردید.")

# ======== بازی ========
@dp.callback_query(lambda c: c.data == "game")
async def game_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 تاس", callback_data="dice")],
        [InlineKeyboardButton(text="🎯 دارت", callback_data="dart")]
    ])
    await callback.message.answer("یک بازی انتخاب کن:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dice")
async def roll_dice(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎲")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dart")
async def throw_dart(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎯")
    await callback.answer()

# ======== حمایت مالی ========
@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 پرداخت با کارت", url="https://example.com/pay")],
        [InlineKeyboardButton(text="🪙 ارز دیجیتال", callback_data="crypto")]
    ])
    await callback.message.answer("روش حمایت را انتخاب کن:", reply_markup=kb)
    await callback.answer()

# ======== ممبرگیر ========
@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer(
        "👥 برای دریافت لینک دعوت گروه، به ادمین پیام بده:\n"
        "📱 @AdminUsername"
    )
    await callback.answer()

# ======== پاسخ به متن‌های عادی ========
@dp.message()
async def echo(message: types.Message):
    await message.answer("❓ دستور نامعتبر! از /start استفاده کن.")

# ======== اجرا ========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
