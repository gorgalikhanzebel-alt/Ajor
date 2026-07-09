const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  userId: { type: Number, unique: true },
  username: String,
  firstName: String,
  lastName: String,
  isAdmin: { type: Boolean, default: false },
  isBanned: { type: Boolean, default: false },
  registeredAt: { type: Date, default: Date.now },
  lastActive: Date,
  messagesCount: { type: Number, default: 0 }
});

module.exports = mongoose.model('User', userSchema);
