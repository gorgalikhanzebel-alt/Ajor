import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from dotenv import load_dotenv
import yt_dlp
import random
import aiosqlite
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# ==================== دیتابیس ====================
async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                join_date TEXT,
                is_banned INTEGER DEFAULT 0
            );
        """)
        await db.commit()

# ==================== منو ====================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😂 جوک", callback_data="joke")],
        [InlineKeyboardButton(text="📥 دانلود", callback_data="download_help")],
        [InlineKeyboardButton(text="🛠 ادمین", callback_data="admin")],
    ])

# ==================== جوک ====================
@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا برنامه‌نویس خسته‌ست؟ چون باگ‌ها خوابش نمی‌برن!", "باگ fix کردم، ۱۰ تا باگ جدید اومد!"]
    await message.answer(random.choice(jokes))

# ==================== دانلودر ====================
@dp.message()
async def downloader(message: types.Message):
    text = message.text or ""
    if any(x in text.lower() for x in ["youtube", "instagram", "tiktok"]):
        await message.answer("⏳ در حال دانلود...")
        # (کد کامل دانلودر رو بعداً کامل می‌کنیم)
        await message.answer("دانلودر فعال شد! لینک رو تست کن.")
    else:
        await message.answer("به ربات خوش اومدی! 🎉\n/joke بزن یا لینک بفرست.", reply_markup=main_menu())

async def main():
    await init_db()
    print("ربات شروع شد!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())