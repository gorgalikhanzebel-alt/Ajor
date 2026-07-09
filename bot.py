import telebot
from telebot import types
import sqlite3
import random
import time
import os
from datetime import datetime

# ==================== CONFIG ====================
TOKEN = "8985557733:AAEQlfffll53QLjNKm8sc3WOM13CIe9Inzw"

bot = telebot.TeleBot(TOKEN)

# Database
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()

# Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    is_admin INTEGER DEFAULT 0,
    join_date TEXT,
    points INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS jokes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
''')

# Default settings
default_settings = {
    'welcome_message': 'سلام! به ربات فوق پیشرفته 🎉 خوش اومدی\nاز منو پایین استفاده کن',
    'max_media_mb': '50'
}

for k, v in default_settings.items():
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

# Sample jokes
sample_jokes = [
    "چرا برنامه‌نویس‌ها عاشق تاریکی هستن؟ چون Light Mode چشمشون رو اذیت می‌کنه!",
    "یه باگ بهم گفت: تو منو پیدا کردی؟ گفتم: بله، حالا برو fix شو!",
    "تلگرام بهتره یا واتساپ؟ هر دو، ولی با این ربات تلگرام خفن‌تره 😎",
    "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود!"
]

for joke in sample_jokes:
    cursor.execute("INSERT OR IGNORE INTO jokes (text) VALUES (?)", (joke,))

conn.commit()

# Create upload folders
os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# ==================== HELPERS ====================
def is_admin(uid):
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (uid,))
    res = cursor.fetchone()
    return res and res[0] == 1

def add_user(user):
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (user_id, username, first_name, join_date) 
        VALUES (?, ?, ?, ?)
    """, (user.id, user.username, user.first_name, datetime.now().isoformat()))
    conn.commit()

def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = cursor.fetchone()
    return res[0] if res else None

# ==================== KEYBOARDS ====================
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add('🎮 بازی‌ها', '🤣 جوک')
    kb.add('📸 آپلود عکس', '🎥 آپلود ویدیو')
    kb.add('📢 کانال', '👥 گروه')
    kb.add('⚙️ تنظیمات', '🛠 ادمین')
    return kb

def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👥 کاربران", callback_data="adm_users"),
        types.InlineKeyboardButton("📊 آمار", callback_data="adm_stats")
    )
    kb.add(
        types.InlineKeyboardButton("📣 پخش همگانی", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("🔧 تنظیمات", callback_data="adm_settings")
    )
    return kb

# ==================== HANDLERS ====================
@bot.message_handler(commands=['start'])
def cmd_start(m):
    add_user(m.from_user)
    bot.send_message(m.chat.id, get_setting('welcome_message'), reply_markup=main_kb())

@bot.message_handler(commands=['admin'])
def cmd_admin(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "⛔ فقط ادمین‌ها دسترسی دارند")
        return
    bot.send_message(m.chat.id, "🛠 پنل ادمین", reply_markup=admin_kb())

# Media Handling
@bot.message_handler(content_types=['photo'])
def save_photo(m):
    add_user(m.from_user)
    file_id = m.photo[-1].file_id
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)
    
    path = f"uploads/photos/{m.from_user.id}_{int(time.time())}.jpg"
    with open(path, 'wb') as f:
        f.write(data)
    
    bot.reply_to(m, f"✅ عکس با موفقیت ذخیره شد!\n📁 {path}")

@bot.message_handler(content_types=['video'])
def save_video(m):
    add_user(m.from_user)
    if m.video.file_size > int(get_setting('max_media_mb')) * 1024*1024:
        bot.reply_to(m, "❌ حجم ویدیو بیش از حد مجاز است!")
        return
    
    file_info = bot.get_file(m.video.file_id)
    data = bot.download_file(file_info.file_path)
    
    path = f"uploads/videos/{m.from_user.id}_{int(time.time())}.mp4"
    with open(path, 'wb') as f:
        f.write(data)
    
    bot.reply_to(m, f"✅ ویدیو با موفقیت ذخیره شد!\n📁 {path}")

# Games & Entertainment
@bot.message_handler(regexp='🎮 بازی‌ها')
def games(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎲 تاس", callback_data="game_dice"))
    kb.add(types.InlineKeyboardButton("❓ جوک کوییز", callback_data="game_jokequiz"))
    bot.send_message(m.chat.id, "🎮 انتخاب بازی:", reply_markup=kb)

@bot.message_handler(regexp='🤣 جوک')
def send_joke(m):
    cursor.execute("SELECT text FROM jokes ORDER BY RANDOM() LIMIT 1")
    joke_text = cursor.fetchone()
    bot.send_message(m.chat.id, f"🤣 {joke_text[0] if joke_text else 'جوک جدیدی پیدا نشد!'}")

# Admin Callbacks
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(c):
    uid = c.from_user.id
    if c.data == "game_dice":
        bot.send_dice(c.message.chat.id)
    elif c.data == "game_jokequiz":
        cursor.execute("SELECT text FROM jokes ORDER BY RANDOM() LIMIT 1")
        joke_text = cursor.fetchone()[0]
        bot.send_message(c.message.chat.id, f"🤔 جوک:\n{joke_text}")
    
    elif c.data.startswith("adm_") and is_admin(uid):
        if c.data == "adm_users":
            cursor.execute("SELECT user_id, username, first_name FROM users LIMIT 20")
            users = cursor.fetchall()
            txt = "👥 کاربران:\n" + "\n".join([f"{u[0]} - @{u[1] or 'بدون یوزرنیم'} {u[2]}" for u in users])
            bot.edit_message_text(txt, c.message.chat.id, c.message.message_id)
        
        elif c.data == "adm_stats":
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            bot.edit_message_text(f"📊 آمار ربات:\nتعداد کل کاربران: {total}", c.message.chat.id, c.message.message_id)
        
        elif c.data == "adm_broadcast":
            msg = bot.send_message(c.message.chat.id, "📣 متن پیام همگانی را ارسال کنید:")
            bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(m):
    if not is_admin(m.from_user.id):
        return
    cursor.execute("SELECT user_id FROM users")
    success = 0
    for (user_id,) in cursor.fetchall():
        try:
            bot.send_message(user_id, m.text)
            success += 1
        except:
            pass
    bot.send_message(m.chat.id, f"✅ پیام به {success} کاربر ارسال شد!")

# Run the bot
if __name__ == "__main__":
    print("🚀 ربات تلگرامی فوق پیشرفته با موفقیت شروع شد!")
    print("📁 پوشه uploads برای ذخیره عکس و ویدیو ایجاد شد.")
    bot.infinity_polling()