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
settings_col = db["settings"]

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

ADMIN_ID = 8985557733  # آیدی عددی خودت رو اینجا بذار (از /profile بگیر)

# ======== منوی اصلی (شیشه‌ای) ========
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📥 دانلود اینستاگرام", callback_data="insta")],
        [InlineKeyboardButton("📤 آپلود فیلم/عکس", callback_data="upload")],
        [InlineKeyboardButton("🎮 بازی و سرگرمی", callback_data="game")],
        [InlineKeyboardButton("💰 حمایت مالی", callback_data="donate")],
        [InlineKeyboardButton("👥 ممبرگیر", callback_data="members")],
        [InlineKeyboardButton("⚙️ پنل ادمین", callback_data="admin_panel")]
    ])

# ======== منوی بازی (شیشه‌ای) ========
def game_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🎲 تاس", callback_data="dice"),
         InlineKeyboardButton("🎯 دارت", callback_data="dart")],
        [InlineKeyboardButton("🎰 شانس", callback_data="slot"),
         InlineKeyboardButton("🃏 ۲۱", callback_data="blackjack")],
        [InlineKeyboardButton("🪨 سنگ‌کاغذ‌قیچی", callback_data="rps")],
        [InlineKeyboardButton("🔢 حدس عدد", callback_data="guess")],
        [InlineKeyboardButton("🏎️ ماشین‌بازی", callback_data="race")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ])

# ======== پنل ادمین (شیشه‌ای) ========
def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📢 ارسال همگانی", callback_data="broadcast")],
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="stats")],
        [InlineKeyboardButton("🚫 مسدودسازی", callback_data="block")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ])

# ======== دستور /start ========
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id, "name": message.from_user.first_name})
    await message.answer(
        f"🚀 سلام {message.from_user.first_name}!\n"
        "به ربات حرفه‌ای من خوش آمدی.\n"
        "از دکمه‌های زیر استفاده کن:",
        reply_markup=main_menu()
    )

# ======== دانلود اینستاگرام با API apido.ir ========
@dp.callback_query(lambda c: c.data == "insta")
async def insta(callback: types.CallbackQuery):
    await callback.message.answer("📎 لینک پست اینستاگرام رو بفرست:")
    await callback.answer()

@dp.message(lambda msg: msg.text and ("instagram.com" in msg.text or "instagr.am" in msg.text))
async def get_insta(message: types.Message):
    url = message.text.strip()
    msg = await message.answer("⏳ در حال دریافت از اینستاگرام...")
    try:
        # استفاده از API رایگان apido.ir
        api_url = f"https://apido.ir/api/instagram/post?url={url}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("data"):
                post = data["data"]
                if post.get("type") == "video":
                    await message.answer_video(post["download_url"], caption="✅ ویدیو دانلود شد!")
                elif post.get("type") == "image":
                    await message.answer_photo(post["download_url"], caption="✅ عکس دانلود شد!")
                else:
                    await message.answer("❌ نوع پست پشتیبانی نمی‌شود.")
                await msg.delete()
                return
        # روش جایگزین: viddownload
        api_url2 = f"https://viddownload.in/api/instagram?url={url}"
        response2 = requests.get(api_url2, timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("success") and data2.get("media"):
                media_url = data2["media"]
                if data2.get("type") == "video":
                    await message.answer_video(media_url, caption="✅ ویدیو دانلود شد!")
                else:
                    await message.answer_photo(media_url, caption="✅ عکس دانلود شد!")
                await msg.delete()
                return
        await message.answer("❌ خطا! لینک معتبر نیست یا اینستاگرام محدودیت ایجاد کرده.")
    except Exception as e:
        logging.error(e)
        await message.answer("❌ خطا! لطفاً لینک را بررسی کن یا بعداً امتحان کن.")
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

@dp.callback_query(lambda c: c.data == "blackjack")
async def blackjack(callback: types.CallbackQuery):
    await callback.message.answer("🃏 بازی ۲۱: عدد ۱ تا ۱۰ رو حدس بزن!")
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
    result = "🤝 مساوی!" if user_choice == bot_choice else "🎉 بردی!" if (user_choice == "🪨 سنگ" and bot_choice == "✂️ قیچی") or (user_choice == "📄 کاغذ" and bot_choice == "🪨 سنگ") or (user_choice == "✂️ قیچی" and bot_choice == "📄 کاغذ") else "😢 باختی!"
    await callback.message.answer(f"تو: {user_choice}\nربات: {bot_choice}\n{result}")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "guess")
async def guess(callback: types.CallbackQuery):
    number = random.randint(1, 10)
    await callback.message.answer(f"🔢 من عدد {number} رو انتخاب کردم!")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "race")
async def race(callback: types.CallbackQuery):
    cars = ["🚗", "🚕", "🚙", "🏎️"]
    winner = random.choice(cars)
    await callback.message.answer(f"🏁 مسابقه تمام شد!\nبرنده: {winner}")
    await callback.answer()

# ======== حمایت مالی ========
@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💳 پرداخت آنلاین", url="https://example.com")],
        [InlineKeyboardButton("🪙 ارز دیجیتال", callback_data="crypto")]
    ])
    await callback.message.answer("💰 روش حمایت را انتخاب کن:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "crypto")
async def crypto(callback: types.CallbackQuery):
    await callback.message.answer("🪙 آدرس کیف‌پول: 0x1234567890abcdef")
    await callback.answer()

# ======== ممبرگیر ========
@dp.callback_query(lambda c: c.data == "members")
async def members(callback: types.CallbackQuery):
    await callback.message.answer("👥 برای لینک دعوت به ادمین پیام بده: @Admin")
    await callback.answer()

# ======== پنل ادمین (فقط برای ادمین) ========
@dp.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ شما دسترسی ندارید!", show_alert=True)
        return
    await callback.message.answer("⚙️ پنل ادمین:", reply_markup=admin_panel())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "broadcast")
async def broadcast(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    await callback.message.answer("📢 پیام همگانی را بنویس:")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "stats")
async def stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    count = users_col.count_documents({})
    await callback.message.answer(f"📊 تعداد کاربران: {count}")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "block")
async def block(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ دسترسی ندارید!", show_alert=True)
        return
    await callback.message.answer("🚫 آیدی کاربر را برای مسدودسازی بفرست:")
    await callback.answer()

# ======== دکمه برگشت ========
@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.answer("🔙 منوی اصلی:", reply_markup=main_menu())
    await callback.answer()

# ======== دستورات جدید ========
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer("📖 راهنما:\n/start - شروع\n/help - راهنما\n/about - درباره ربات\n/ping - بررسی وضعیت\n/time - ساعت و تاریخ\n/profile - آیدی من\n/stat - آمار ربات\n/joke - جوک تصادفی\n/quote - نقل قول انگیزشی")

@dp.message(Command("about"))
async def about(message: types.Message):
    await message.answer("🤖 ربات حرفه‌ای\nساخته شده با aiogram و عشق ❤️")

@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("✅ ربات آنلاین است!")

@dp.message(Command("time"))
async def time_command(message: types.Message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await message.answer(f"🕒 زمان: {now}")

@dp.message(Command("profile"))
async def profile(message: types.Message):
    await message.answer(f"👤 نام: {message.from_user.full_name}\n🆔 آیدی: {message.from_user.id}")

@dp.message(Command("stat"))
async def stat(message: types.Message):
    count = users_col.count_documents({})
    await message.answer(f"📊 کاربران: {count}")

@dp.message(Command("joke"))
async def joke(message: types.Message):
    jokes = ["چرا مرغ از جاده رد شد؟ برای اینکه به اون طرف برسه! 😂", "بهترین زبان برنامه‌نویسی؟ پایتون! 🐍", "ربات خوب، رباتی که جواب بده!"]
    await message.answer(random.choice(jokes))

@dp.message(Command("quote"))
async def quote(message: types.Message):
    quotes = ["همیشه به فکر فردا باش!", "موفقیت یعنی بلند شدن دوباره!", "کد بزن و لذت ببر!"]
    await message.answer(f"💬 {random.choice(quotes)}")

# ======== پیام‌های دیگر ========
@dp.message()
async def unknown(message: types.Message):
    await message.answer("❌ دستور نامعتبر!\nاز /start استفاده کن یا دکمه‌ها رو بزن.")

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