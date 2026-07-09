import asyncio
import os
import logging
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
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
groups_col = db["groups"]

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

ADMIN_ID = 466050034

# ======== بررسی ادمین بودن در گروه ========
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

# ======== منوهای شیشه‌ای ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton(text="🎮 بازی", callback_data="game")],
        [InlineKeyboardButton(text="⚙️ مدیریت گروه", callback_data="group_manage")],
        [InlineKeyboardButton(text="⚙️ پنل ادمین", callback_data="admin_panel")]
    ])

def group_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔒 قفل گروه", callback_data="lock_group"),
         InlineKeyboardButton("🔓 باز کردن گروه", callback_data="unlock_group")],
        [InlineKeyboardButton("🚫 بن کاربر", callback_data="ban_user"),
         InlineKeyboardButton("✅ رفع بن", callback_data="unban_user")],
        [InlineKeyboardButton("🧹 پاک کردن پیام‌ها", callback_data="clear_messages")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
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
        "به ربات مدیریت گروه خوش آمدی.\n"
        "از دکمه‌ها استفاده کن:",
        reply_markup=main_menu()
    )

# ======== مدیریت گروه ========
@dp.callback_query(lambda c: c.data == "group_manage")
async def group_manage(callback: types.CallbackQuery):
    await callback.message.answer("⚙️ مدیریت گروه:", reply_markup=group_menu())
    await callback.answer()

# ======== قفل و باز کردن گروه ========
@dp.callback_query(lambda c: c.data == "lock_group")
async def lock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=False))
    await callback.message.answer("🔒 گروه قفل شد. فقط ادمین‌ها می‌تونن پیام بدن.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "unlock_group")
async def unlock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=True))
    await callback.message.answer("🔓 گروه باز شد. همه می‌تونن پیام بدن.")
    await callback.answer()

# ======== بن و رفع بن ========
@dp.callback_query(lambda c: c.data == "ban_user")
async def ban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("🚫 آیدی عددی کاربر رو برای بن کردن بفرست:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "unban_user")
async def unban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("✅ آیدی عددی کاربر رو برای رفع بن بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and msg.text.isdigit() and "بن" in msg.text)
async def handle_ban(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    user_id = int(message.text)
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"✅ کاربر {user_id} بن شد.")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")

@dp.message(lambda msg: msg.text and msg.text.isdigit() and "رفع بن" in msg.text)
async def handle_unban(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    user_id = int(message.text)
    try:
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"✅ بن کاربر {user_id} رفع شد.")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")

# ======== پاک کردن پیام‌ها ========
@dp.callback_query(lambda c: c.data == "clear_messages")
async def clear_messages(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("🧹 تعداد پیام‌ها رو برای پاک کردن بفرست (مثلاً 10):")
    await callback.answer()

@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def handle_clear(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    count = int(message.text)
    if count > 100:
        await message.answer("❌ حداکثر ۱۰۰ پیام می‌تونی پاک کنی.")
        return
    deleted = 0
    async for msg in bot.get_chat_history(message.chat.id, limit=count):
        if msg.message_id != message.message_id:
            await msg.delete()
            deleted += 1
    await message.answer(f"✅ {deleted} پیام پاک شد.")

# ======== خوش‌آمدگویی خودکار ========
@dp.message()
async def welcome_new_member(message: types.Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            await message.answer(f"👋 به گروه خوش آمدی {member.full_name}!\nلطفاً قوانین رو رعایت کن.")

# ======== حذف پیام‌های دارای لینک یا کلمات ممنوع ========
@dp.message()
async def filter_messages(message: types.Message):
    if message.chat.type != "private":
        blocked_words = ["تبلیغ", "سئو", "لینک", "https://", "http://"]
        if any(word in message.text.lower() for word in blocked_words):
            if not await is_admin(message.chat.id, message.from_user.id):
                await message.delete()
                await message.answer("❌ پیام شما حاوی لینک یا کلمه ممنوعه بود و حذف شد.")

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
    if message.chat.type == "private":
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