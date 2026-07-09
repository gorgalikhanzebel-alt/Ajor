import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("❌ توکن تنظیم نشده!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ======== تابع بررسی ادمین ========
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

# ======== منوی مدیریت گروه ========
def group_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔒 قفل گروه", callback_data="lock")],
        [InlineKeyboardButton("🔓 باز کردن گروه", callback_data="unlock")],
        [InlineKeyboardButton("🚫 بن کاربر", callback_data="ban")],
        [InlineKeyboardButton("✅ رفع بن", callback_data="unban")],
        [InlineKeyboardButton("🧹 پاک کردن پیام‌ها", callback_data="clear")]
    ])

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    if message.chat.type == "private":
        await message.answer("👋 سلام! من ربات مدیریت گروه هستم. لطفاً مرا به گروه اضافه کن و ادمین کن.")
    else:
        await message.answer("🤖 ربات مدیریت گروه فعال است.", reply_markup=group_menu())

# ======== قفل ========
@dp.callback_query(lambda c: c.data == "lock")
async def lock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=False))
    await callback.message.answer("🔒 گروه قفل شد.")
    await callback.answer()

# ======== باز کردن ========
@dp.callback_query(lambda c: c.data == "unlock")
async def unlock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=True))
    await callback.message.answer("🔓 گروه باز شد.")
    await callback.answer()

# ======== بن ========
@dp.callback_query(lambda c: c.data == "ban")
async def ban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("🚫 آیدی عددی کاربر رو به‌صورت زیر بفرست:\n`/ban 123456789`")
    await callback.answer()

@dp.message(Command("ban"))
async def ban_cmd(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    try:
        user_id = int(message.text.split()[1])
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"✅ کاربر {user_id} بن شد.")
    except:
        await message.answer("❌ فرمت صحیح: `/ban 123456789`")

# ======== رفع بن ========
@dp.callback_query(lambda c: c.data == "unban")
async def unban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("✅ آیدی عددی کاربر رو به‌صورت زیر بفرست:\n`/unban 123456789`")
    await callback.answer()

@dp.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    try:
        user_id = int(message.text.split()[1])
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"✅ بن کاربر {user_id} رفع شد.")
    except:
        await message.answer("❌ فرمت صحیح: `/unban 123456789`")

# ======== پاک کردن پیام‌ها ========
@dp.callback_query(lambda c: c.data == "clear")
async def clear_messages(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("🧹 تعداد پیام‌ها رو بفرست (مثلاً `10`):")
    await callback.answer()

@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def clear_cmd(message: types.Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer("⛔ فقط ادمین‌ها!")
        return
    count = int(message.text)
    if count > 100:
        await message.answer("❌ حداکثر ۱۰۰ پیام.")
        return
    deleted = 0
    async for msg in bot.get_chat_history(message.chat.id, limit=count):
        if msg.message_id != message.message_id:
            await msg.delete()
            deleted += 1
    await message.answer(f"✅ {deleted} پیام پاک شد.")

# ======== خوش‌آمدگویی ========
@dp.message()
async def welcome(message: types.Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            await message.answer(f"👋 به گروه خوش آمدی {member.full_name}!")

# ======== فیلتر لینک ========
@dp.message()
async def filter_links(message: types.Message):
    if message.chat.type != "private":
        if message.text and ("http" in message.text or "www." in message.text):
            if not await is_admin(message.chat.id, message.from_user.id):
                await message.delete()
                await message.answer("❌ ارسال لینک ممنوع!", reply_to_message_id=message.message_id)

# ======== پورت ========
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

async def main():
    await start_web()
    logging.info("🤖 Starting bot...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())