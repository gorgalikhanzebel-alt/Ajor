const User = require('../models/User');

module.exports = async function authMiddleware(req, res, next) {
  const { message } = req.body;
  if (message) {
    const userId = message.from.id;
    const user = await User.findOne({ userId });

    if (user && user.isBanned) {
      const botToken = process.env.BOT_TOKEN;
      const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
      await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: message.chat.id,
          text: '⛔ شما مسدود شده‌اید.'
        })
      });
      return res.sendStatus(200);
    }
  }
  next();
};
