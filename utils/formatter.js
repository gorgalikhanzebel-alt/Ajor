module.exports = {
  bold: (text) => `*${text}*`,
  italic: (text) => `_${text}_`,
  code: (text) => `\`${text}\``,
  link: (text, url) => `[${text}](${url})`
};
