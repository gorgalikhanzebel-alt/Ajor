const mongoose = require('mongoose');
const config = require('../config/settings');

async function connectDB() {
  try {
    await mongoose.connect(config.mongoUri);
    console.log('✅ به MongoDB متصل شدیم!');
  } catch (error) {
    console.error('❌ خطا در اتصال به MongoDB:', error);
    process.exit(1);
  }
}

module.exports = { connectDB };
