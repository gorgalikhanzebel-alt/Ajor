require('dotenv').config();

module.exports = {
  botToken: process.env.BOT_TOKEN,
  mongoUri: process.env.MONGODB_URI,
  adminId: parseInt(process.env.ADMIN_ID),
  channelId: process.env.CHANNEL_ID,
  aiApiKey: process.env.AI_API_KEY,
  port: process.env.PORT || 3000,
  webhookPath: '/webhook'
};
