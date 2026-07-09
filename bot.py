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

ADMIN_ID = 466050034  # آیدی شما

# ======== منوهای شیشه‌ای ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 دانلود اینستاگرام", callback_data="insta")],
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

def admin_panel_menu():
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
        f"سلام {message.from_user.first_name}! به ربات خوش آمدی 🚀",
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
    await message.answer("⏳ در حال دریافت از اینستاگرام...")
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
                return
        await message.answer("❌ خطا! لینک معتبر نیست.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لطفاً لینک را بررسی کن.")

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

@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.answer("🔙 منوی اصلی:", reply_markup=main_menu())
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

# ======== پنل ادمین (فقط برای شما) ========
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

# ======== دستورات کامل ========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 لیست دستورات:\n"
        "/start - شروع و منوی اصلی\n"
        "/help - نمایش راهنما\n"
        "/about - درباره ربات\n"
        "/ping - بررسی وضعیت\n"
        "/time - ساعت و تاریخ\n"
        "/id - آیدی عددی شما\n"
        "/profile - پروفایل شما\n"
        "/stat - آمار کاربران\n"
        "/joke - جوک تصادفی\n"
        "/quote - نقل قول انگیزشی\n"
        "/admin - پنل ادمین"
    )

@dp.message(Command("about"))
async def about(message: types.Message):
    await message.answer("🤖 این ربات با aiogram ساخته شده و شامل بازی‌ها، دانلود اینستاگرام، و مدیریت گروه است.")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("✅ ربات آنلاین است!")

@dp.message(Command("time"))
async def time_command(message: types.Message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(f"🕒 {now}")

@dp.message(Command("id"))
async def id_command(message: types.Message):
    await message.answer(f"🆔 آیدی عددی شما: `{message.from_user.id}`")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    await message.answer(f"👤 نام: {message.from_user.full_name}\n🆔 آیدی: {message.from_user.id}")

@dp.message(Command("stat"))
async def stat(message: types.Message):
    count = users_col.count_documents({})
    await message.answer(f"📊 تعداد کاربران: {count}")

@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا مرغ از جاده رد شد؟ 😂", "پایتون بهترین زبان!", "ربات خوب رباتی که جواب بده!"]
    await message.answer(random.choice(jokes))

@dp.message(Command("quote"))
async def quote(message: types.Message):
    quotes = ["همیشه به فکر فردا باش!", "موفقیت یعنی بلند شدن دوباره!", "کد بزن و لذت ببر!"]
    await message.answer(f"💬 {random.choice(quotes)}")

@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ شما دسترسی به پنل ادمین ندارید!")
        return
    await message.answer("⚙️ پنل ادمین:", reply_markup=admin_panel_menu())

# ======== پیام‌های دیگر ========
@dp.message()
async def unknown(message: types.Message):
    if message.chat.type == "private":
        await message.answer("❌ دستور نامعتبر! از /start استفاده کن یا /help بزن.")

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