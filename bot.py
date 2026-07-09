import asyncio
import logging
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from dotenv import load_dotenv
import yt_dlp
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
MONGO_URI = os.getenv("MONGO_URI")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# ==================== MongoDB ====================
client = AsyncIOMotorClient(MONGO_URI)
db = client["AjorBot"]

async def add_user(user: types.User):
    await db.users.update_one(
        {"user_id": user.id},
        {"$set": {
            "username": user.username,
            "first_name": user.first_name,
            "join_date": datetime.now()
        }},
        upsert=True
    )

# ==================== منو ====================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😂 جوک", callback_data="joke")],
        [InlineKeyboardButton(text="📥 دانلودر", callback_data="download")],
        [InlineKeyboardButton(text="🛠 ادمین", callback_data="admin")]
    ])

# ==================== جوک ====================
@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا برنامه‌نویس خسته‌ست؟ چون باگ‌ها خوابش نمی‌برن!", "fix کردم، ۱۰ تا باگ جدید اومد!"]
    await message.answer(random.choice(jokes))

# ==================== دانلودر ====================
@dp.message()
async def handle_message(message: types.Message):
    await add_user(message.from_user)
    text = message.text or ""

    if any(x in text.lower() for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        await message.answer("⏳ در حال دانلود...")
        # دانلودر (بعداً کامل‌تر می‌کنیم)
        await message.answer("دانلودر در حال توسعه است...")
        return

    await message.answer("به سوپر ربات Ajor خوش اومدی 🚀", reply_markup=main_menu())

async def main():
    print("🤖 سوپر ربات Ajor آنلاین شد!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())