const mongoose = require('mongoose');

const fileSchema = new mongoose.Schema({
  userId: Number,
  fileId: String,
  fileType: String,
  caption: String,
  date: { type: Date, default: Date.now }
});

module.exports = mongoose.model('File', fileSchema);
