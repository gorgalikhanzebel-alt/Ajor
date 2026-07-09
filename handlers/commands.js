const User = require('../models/User');
const start = require('../commands/user/start');
const help = require('../commands/user/help');
const about = require('../commands/user/about');
const ping = require('../commands/user/ping');
const time = require('../commands/user/time');
const id = require('../commands/user/id');
const profile = require('../commands/user/profile');
const stats = require('../commands/user/stats');
const ban = require('../commands/admin/ban');
const unban = require('../commands/admin/unban');
const broadcast = require('../commands/admin/broadcast');
const adminPanel = require('../commands/admin/adminPanel');
const joke = require('../commands/fun/joke');
const quote = require('../commands/fun/quote');

module.exports = async function handleCommand(message, sendMessage, sendPhoto, sendVideo, sendDocument) {
  const chatId = message.chat.id;
  const text = message.text;
  const userId = message.from.id;

  const user = await User.findOne({ userId });
  const isAdmin = user && user.isAdmin;

  switch (text) {
    case '/start': return await start(message, sendMessage);
    case '/help': return await help(message, sendMessage);
    case '/about': return await about(message, sendMessage);
    case '/ping': return await ping(message, sendMessage);
    case '/time': return await time(message, sendMessage);
    case '/id': return await id(message, sendMessage);
    case '/profile': return await profile(message, sendMessage);
    case '/stats': return await stats(message, sendMessage, isAdmin);
    case '/joke': return await joke(message, sendMessage);
    case '/quote': return await quote(message, sendMessage);
    case '/admin': return await adminPanel(message, sendMessage, isAdmin);
    default:
      if (isAdmin) {
        if (text.startsWith('/ban ')) return await ban(message, sendMessage);
        if (text.startsWith('/unban ')) return await unban(message, sendMessage);
        if (text.startsWith('/broadcast ')) return await broadcast(message, sendMessage);
      }
      return await sendMessage(chatId, `✅ پیام شما دریافت شد.`);
  }
};
