const User = require('../models/User');

module.exports = {
  formatDate: (date) => new Date(date).toLocaleDateString('fa-IR'),
  formatTime: (date) => new Date(date).toLocaleTimeString('fa-IR'),
  randomInt: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,
  shuffleArray: (arr) => arr.sort(() => Math.random() - 0.5),
  
  registerUser: async (message) => {
    const userId = message.from.id;
    const username = message.from.username || '';
    const firstName = message.from.first_name || '';
    const lastName = message.from.last_name || '';

    const existingUser = await User.findOne({ userId });
    if (!existingUser) {
      const newUser = new User({ userId, username, firstName, lastName });
      await newUser.save();
      return true;
    } else {
      existingUser.lastActive = new Date();
      existingUser.messagesCount += 1;
      await existingUser.save();
      return false;
    }
  }
};
