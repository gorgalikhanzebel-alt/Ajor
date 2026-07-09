const mongoose = require('mongoose');

async function connectDB() {
  // اگر متغیر محیطی نبود، از این آدرس مستقیم استفاده کن
  const uri = process.env.MONGODB_URI || 'mongodb+srv://gorgalikhanzebel_db_user:ZZ8O2D3VhzPgqHxZ@cluster0.y56mkjn.mongodb.net/?appName=Cluster0';
  
  try {
    await mongoose.connect(uri);
    console.log('✅ به MongoDB متصل شدیم!');
  } catch (error) {
    console.error('❌ خطا در اتصال به MongoDB:', error);
    process.exit(1);
  }
}

module.exports = { connectDB };
