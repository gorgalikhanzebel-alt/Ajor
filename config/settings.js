require('dotenv').config();

module.exports = {
  botToken: process.env.BOT_TOKEN,
  mongoUri: process.env.MONGODB_URI || 'mongodb+srv://gorgalikhanzebel_db_user:ZZ8O2D3VhzPgqHxZ@cluster0.y56mkjn.mongodb.net/?appName=Cluster0',
  adminId: parseInt(process.env.ADMIN_ID) || 0,
  channelId: process.env.CHANNEL_ID,
  aiApiKey: process.env.AI_API_KEY,
  port: process.env.PORT || 3000
};
