import asyncio
import os
import logging
import random
import requests
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

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

ADMIN_ID = 466050034  # آیدی عددی خودت

# ======== توابع کمکی ========
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except:
        return False

# ======== منوهای شیشه‌ای ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton("📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton("🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton("💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton("👥 ممبرگیر", callback_data="members")],
        [InlineKeyboardButton("⚙️ مدیریت گروه", callback_data="group_manage")],
        [InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")]
    ])

def game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🎲 تاس", callback_data="dice"),
         InlineKeyboardButton("🎯 دارت", callback_data="dart")],
        [InlineKeyboardButton("🎰 شانس", callback_data="slot")],
        [InlineKeyboardButton("🪨 سنگ‌کاغذ‌قیچی", callback_data="rps")],
        [InlineKeyboardButton("🔢 حدس عدد", callback_data="guess")],
        [InlineKeyboardButton("🏎️ ماشین‌بازی", callback_data="race")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
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

def admin_panel_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ])

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(
        f"🚀 سلام {message.from_user.first_name}!\nبه ربات خوش آمدی.",
        reply_markup=main_menu()
    )

# ======== دانلود اینستاگرام ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت از اینستاگرام...")
    try:
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
        await message.answer("❌ خطا! لینک معتبر نیست یا محدودیت ایجاد شده.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لطفاً بعداً امتحان کن.")
    await msg.delete()

# ======== آپلود ========
@dp.callback_query(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("📤 فیلم یا عکس خود را بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.photo or msg.video)
async def handle_media(message: types.Message):
    if message.photo:
        await message.answer("✅ عکس شما دریافت شد!")
    elif message.video:
        await message.answer("✅ فیلم شما دریافت شد!")

# ======== بازی‌ها ========
@dp.callback_query(lambda c: c.data == "game")
async def game(callback: types.CallbackQuery):
    await callback.message.answer("🎮 یک بازی انتخاب کن:", reply_markup=game_menu())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dice")
async def dice(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎲")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "dart")
async def dart(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎯")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "slot")
async def slot(callback: types.CallbackQuery):
    await callback.message.answer_dice(emoji="🎰")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "rps")
async def rps(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🪨 سنگ", callback_data="rps_stone"),
         InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
         InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors")]
    ])
    await callback.message.answer("یکی رو انتخاب کن:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("rps_"))
async def rps_play(callback: types.CallbackQuery):
    choices = {"rps_stone": "🪨 سنگ", "rps_paper": "📄 کاغذ", "rps_scissors": "✂️ قیچی"}
    bot_choice = random.choice(list(choices.values()))
    user_choice = choices[callback.data]
    if user_choice == bot_choice:
        result = "🤝 مساوی!"
    elif (user_choice == "🪨 سنگ" and bot_choice == "✂️ قیچی") or \
         (user_choice == "📄 کاغذ" and bot_choice == "🪨 سنگ") or \
         (user_choice == "✂️ قیچی" and bot_choice == "📄 کاغذ"):
        result = "🎉 بردی!"
    else:
        result = "😢 باختی!"
    await callback.message.answer(f"تو: {user_choice}\nربات: {bot_choice}\n{result}")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "guess")
async def guess(callback: types.CallbackQuery):
    number = random.randint(1, 10)
    await callback.message.answer(f"🔢 من عدد {number} رو انتخاب کردم!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "race")
async def race(callback: types.CallbackQuery):
    winner = random.choice(["🚗", "🚕", "🚙", "🏎️"])
    await callback.message.answer(f"🏁 برنده مسابقه: {winner}")
    await callback.answer()

# ======== حمایت مالی ========
@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    await callback.message.answer("💳 لینک حمایت: https://example.com")
    await callback.answer()

# ======== ممبرگیر ========
@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer("👥 لینک دعوت: @Admin")
    await callback.answer()

# ======== مدیریت گروه ========
@dp.callback_query(lambda c: c.data == "group_manage")
async def group_manage(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("⚙️ مدیریت گروه:", reply_markup=group_menu())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "lock_group")
async def lock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=False))
    await callback.message.answer("🔒 گروه قفل شد.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "unlock_group")
async def unlock_group(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await bot.set_chat_permissions(callback.message.chat.id, ChatPermissions(can_send_messages=True))
    await callback.message.answer("🔓 گروه باز شد.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "ban_user")
async def ban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("🚫 آیدی عددی کاربر را به‌صورت `/ban 123456789` بفرست:")
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

@dp.callback_query(lambda c: c.data == "unban_user")
async def unban_user(callback: types.CallbackQuery):
    if not await is_admin(callback.message.chat.id, callback.from_user.id):
        await callback.answer("⛔ فقط ادمین‌ها!", show_alert=True)
        return
    await callback.message.answer("✅ آیدی عددی کاربر را به‌صورت `/unban 123456789` بفرست:")
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

@dp.callback_query(lambda c: c.data == "clear_messages")
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
    if message.chat.type != "private" and message.text:
        if "http" in message.text or "www." in message.text:
            if not await is_admin(message.chat.id, message.from_user.id):
                await message.delete()
                await message.answer("❌ ارسال لینک ممنوع!", reply_to_message_id=message.message_id)

# ======== پنل ادمین ========
@dp.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    await callback.message.answer("⚙️ پنل ادمین:", reply_markup=admin_panel_menu())
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

# ======== دستورات جانبی ========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("📖 راهنما:\n/start - شروع\n/help - راهنما\n/profile - آیدی من\n/time - ساعت\n/joke - جوک")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    await message.answer(f"👤 نام: {message.from_user.full_name}\n🆔 آیدی: {message.from_user.id}")

@dp.message(Command("time"))
async def time_command(message: types.Message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(f"🕒 {now}")

@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا مرغ از جاده رد شد؟ 😂", "پایتون بهترین زبان!", "ربات خوب رباتی که جواب بده!"]
    await message.answer(random.choice(jokes))

# ======== پیام‌های دیگر ========
@dp.message()
async def unknown(message: types.Message):
    if message.chat.type == "private":
        await message.answer("❌ دستور نامعتبر! از /start استفاده کن.")

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