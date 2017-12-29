var mongoose = require('mongoose');

var ratingScheme = new mongoose.Schema({
    uid: { type: Number},
    movie_id: { type: Number},
    rating: { type: Number},
}, { timestamps: true });

var Ratings = mongoose.model('ratings', ratingScheme);

module.exports = Ratings;
