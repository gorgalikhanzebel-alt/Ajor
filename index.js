const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

// --- متغیرهای محیطی ---
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb+srv://gorgalikhanzebel_db_user:ZZ8O2D3VhzPgqHxZ@cluster0.y56mkjn.mongodb.net/?appName=Cluster0';
const BOT_TOKEN = process.env.BOT_TOKEN || '8985557733:AAGN4ZraC4fnc2PCm7eAOwAV-TkL0yl4L-Y';
const ADMIN_ID = process.env.ADMIN_ID || 123456789; // آیدی عددی ادمین

// --- اتصال به MongoDB ---
mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ به MongoDB متصل شدیم!'))
  .catch(err => console.error('❌ خطا در اتصال به MongoDB:', err));

// --- مدل‌های دیتابیس ---
const userSchema = new mongoose.Schema({
  userId: Number,
  username: String,
  firstName: String,
  lastName: String,
  isAdmin: { type: Boolean, default: false },
  registeredAt: { type: Date, default: Date.now },
  lastActive: Date,
  messagesCount: { type: Number, default: 0 }
});
const User = mongoose.model('User', userSchema);

const fileSchema = new mongoose.Schema({
  userId: Number,
  fileId: String,
  fileType: String,
  caption: String,
  date: { type: Date, default: Date.now }
});
const File = mongoose.model('File', fileSchema);

const messageSchema = new mongoose.Schema({
  userId: Number,
  message: String,
  date: { type: Date, default: Date.now }
});
const Message = mongoose.model('Message', messageSchema);

// --- توابع کمکی ---
async function sendMessage(chatId, text, options = {}) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text, ...options })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال پیام:', error);
  }
}

async function sendPhoto(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, photo: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال عکس:', error);
  }
}

async function sendVideo(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendVideo`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, video: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال فیلم:', error);
  }
}

async function sendDocument(chatId, fileId, caption = '') {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendDocument`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, document: fileId, caption })
    });
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در ارسال فایل:', error);
  }
}

async function getFile(fileId) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`;
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error('❌ خطا در دریافت فایل:', error);
  }
}

// --- مدیریت کاربران ---
async function registerUser(message) {
  const userId = message.from.id;
  const username = message.from.username || '';
  const firstName = message.from.first_name || '';
  const lastName = message.from.last_name || '';

  const existingUser = await User.findOne({ userId });
  if (!existingUser) {
    const newUser = new User({ userId, username, firstName, lastName });
    await newUser.save();
    return true; // کاربر جدید
  } else {
    existingUser.lastActive = new Date();
    existingUser.messagesCount += 1;
    await existingUser.save();
    return false; // کاربر قبلی
  }
}

// --- مدیریت دستورات ---
async function handleCommand(message) {
  const chatId = message.chat.id;
  const text = message.text;
  const userId = message.from.id;

  // بررسی ادمین
  const user = await User.findOne({ userId });
  const isAdmin = user && user.isAdmin;

  switch (text) {
    case '/start':
      await sendMessage(chatId, `👋 سلام ${message.from.first_name}!\nبه ربات فوق‌العاده خوش آمدید.\nلیست دستورات: /help`);
      break;

    case '/help':
      await sendMessage(chatId, `📖 **راهنمای کامل:**\n
      /start - شروع و خوش‌آمدگویی
      /help - نمایش این راهنما
      /about - درباره ربات
      /ping - بررسی وضعیت
      /time - ساعت و تاریخ
      /id - نمایش آیدی شما
      /profile - پروفایل شما
      /stats - آمار ربات
      
      **📁 مدیریت فایل:**
      ارسال عکس، فیلم، سند - آپلود خودکار
      /forward - ارسال فایل به کانال (به همراه آیدی فایل)
      
      **🎮 سرگرمی:**
      /joke - جوک تصادفی
      /quote - نقل قول انگیزشی
      
      **👑 ادمین:**
      /admin - پنل ادمین (فقط ادمین)
      /ban [userId] - مسدود کردن کاربر
      /unban [userId] - رفع مسدودی
      /broadcast [پیام] - ارسال به همه کاربران
      /stats - آمار کامل`);
      break;

    case '/about':
      await sendMessage(chatId, `🤖 **ربات فوق‌العاده**\nنسخه 3.0\nساخته شده با Node.js + MongoDB\nتوسعه‌دهنده: @gorgalikhanzebel`);
      break;

    case '/ping':
      await sendMessage(chatId, '🏓 پُنگ! ربات فعال است.');
      break;

    case '/time':
      const now = new Date();
      const timeStr = now.toLocaleString('fa-IR', { timeZone: 'Asia/Tehran' });
      await sendMessage(chatId, `🕐 زمان فعلی: ${timeStr}`);
      break;

    case '/id':
      await sendMessage(chatId, `🆔 آیدی شما: ${userId}`);
      break;

    case '/profile':
      const userData = await User.findOne({ userId });
      if (userData) {
        const profileText = `👤 **پروفایل شما:**\n
        آیدی: ${userData.userId}
        نام کاربری: @${userData.username || 'ندارد'}
        نام: ${userData.firstName || 'ندارد'} ${userData.lastName || ''}
        تعداد پیام‌ها: ${userData.messagesCount}
        تاریخ ثبت‌نام: ${new Date(userData.registeredAt).toLocaleDateString('fa-IR')}`;
        await sendMessage(chatId, profileText);
      }
      break;

    case '/stats':
      if (isAdmin) {
        const totalUsers = await User.countDocuments();
        const totalMessages = await Message.countDocuments();
        const totalFiles = await File.countDocuments();
        const statsText = `📊 **آمار ربات:**\n
        👥 کاربران: ${totalUsers}
        💬 پیام‌ها: ${totalMessages}
        📁 فایل‌ها: ${totalFiles}
        🚀 وضعیت: آنلاین`;
        await sendMessage(chatId, statsText);
      } else {
        await sendMessage(chatId, '⚠️ این دستور فقط برای ادمین است.');
      }
      break;

    case '/joke':
      const jokes = [
        'چرا برنامه‌نویس‌ها عاشق طبیعت‌اند؟ چون همه جا null هست!',
        'تفاوت بین یه برنامه‌نویس و یه مهندس؟ برنامه‌نویس فکر میکنه 0=1، مهندس میدونه 1=0!',
        'بهترین زبان برنامه‌نویسی کدام است؟ زبانی که رئیست بلد نیست!'
      ];
      const randomJoke = jokes[Math.floor(Math.random() * jokes.length)];
      await sendMessage(chatId, `😂 ${randomJoke}`);
      break;

    case '/quote':
      const quotes = [
        '✨ موفقیت مجموع تلاش‌های کوچک روزانه است.',
        '💪 تنها راه انجام کار عالی این است که کاری را که دوست داری انجام دهی.',
        '🌟 آینده متعلق به کسانی است که به رویاهای خود ایمان دارند.'
      ];
      const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
      await sendMessage(chatId, randomQuote);
      break;

    case '/admin':
      if (isAdmin) {
        await sendMessage(chatId, `👑 **پنل ادمین:**\n
        /ban [userId] - مسدود کردن کاربر
        /unban [userId] - رفع مسدودی
        /broadcast [پیام] - ارسال به همه
        /stats - آمار کامل`);
      } else {
        await sendMessage(chatId, '⚠️ شما دسترسی ادمین ندارید.');
      }
      break;

    default:
      // بررسی دستورات ادمین
      if (isAdmin) {
        if (text.startsWith('/ban ')) {
          const targetId = parseInt(text.split(' ')[1]);
          if (targetId) {
            await User.findOneAndUpdate({ userId: targetId }, { isBanned: true });
            await sendMessage(chatId, `✅ کاربر ${targetId} مسدود شد.`);
          }
        } else if (text.startsWith('/unban ')) {
          const targetId = parseInt(text.split(' ')[1]);
          if (targetId) {
            await User.findOneAndUpdate({ userId: targetId }, { isBanned: false });
            await sendMessage(chatId, `✅ کاربر ${targetId} رفع مسدودی شد.`);
          }
        } else if (text.startsWith('/broadcast ')) {
          const broadcastMessage = text.slice(11);
          const allUsers = await User.find({});
          let sentCount = 0;
          for (const user of allUsers) {
            try {
              await sendMessage(user.userId, `📢 **پیام همگانی:**\n${broadcastMessage}`);
              sentCount++;
            } catch (error) {
              console.error(`❌ خطا در ارسال به ${user.userId}`);
            }
          }
          await sendMessage(chatId, `✅ پیام به ${sentCount} کاربر ارسال شد.`);
        }
      }
  }
}

// --- مدیریت فایل‌ها ---
async function handleFile(message) {
  const chatId = message.chat.id;
  const userId = message.from.id;
  let fileId = null;
  let fileType = null;
  let caption = message.caption || '';

  if (message.photo) {
    fileId = message.photo[message.photo.length - 1].file_id;
    fileType = 'photo';
  } else if (message.video) {
    fileId = message.video.file_id;
    fileType = 'video';
  } else if (message.document) {
    fileId = message.document.file_id;
    fileType = 'document';
  } else {
    return false;
  }

  // ذخیره در دیتابیس
  try {
    const newFile = new File({ userId, fileId, fileType, caption });
    await newFile.save();
  } catch (error) {
    console.error('❌ خطا در ذخیره فایل:', error);
  }

  await sendMessage(chatId, `✅ فایل شما با موفقیت دریافت شد.\nنوع: ${fileType}\nآیدی فایل: \`${fileId}\``, { parse_mode: 'Markdown' });
  return true;
}

// --- Webhook اصلی ---
app.post('/webhook', async (req, res) => {
  const { message } = req.body;
  if (!message) {
    res.sendStatus(200);
    return;
  }

  const userId = message.from.id;

  // ثبت کاربر در دیتابیس
  await registerUser(message);

  // بررسی مسدودی
  const user = await User.findOne({ userId });
  if (user && user.isBanned) {
    await sendMessage(message.chat.id, '⛔ شما مسدود شده‌اید.');
    res.sendStatus(200);
    return;
  }

  // مدیریت دستورات
  if (message.text && message.text.startsWith('/')) {
    await handleCommand(message);
  }
  // مدیریت فایل‌ها
  else if (message.photo || message.video || message.document) {
    await handleFile(message);
  }
  // پیام معمولی
  else if (message.text) {
    // ذخیره در دیتابیس
    try {
      const newMessage = new Message({ userId, message: message.text });
      await newMessage.save();
    } catch (error) {
      console.error('❌ خطا در ذخیره پیام:', error);
    }

    await sendMessage(message.chat.id, `✅ پیام شما دریافت شد.`);
  }

  res.sendStatus(200);
});

app.get('/', (req, res) => {
  res.send('🤖 ربات فوق‌العاده فعال است!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 ربات فوق‌العاده روی پورت ${PORT} در حال اجراست`);
});
