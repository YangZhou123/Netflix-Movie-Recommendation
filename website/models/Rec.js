var mongoose = require('mongoose');

var recSchema = new mongoose.Schema({
    uid: Number,
    mid: [Number],
    time: Date
});

var recs = mongoose.model('recs', recSchema);

module.exports = recs;