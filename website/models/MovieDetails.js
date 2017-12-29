var mongoose = require('mongoose');
var random = require('mongoose-simple-random');

var movieDetailsSchema = new mongoose.Schema({
    id: { type: String, unique: true },
    Plot: { type: String},
    Poster: { type: String},
    Country: { type: String},
    Writer: { type: String},
    Metascore: { type: String},
    Director: { type: String},
    Released: { type: String},
    Actors: { type: String},
    imdbRating: { type: String},
    Year: { type: String},
    Genre: { type: String},
    Awards: { type: String},
    Awards: { type: String},
    Runtime: { type: String},
    Type: { type: String},
    Response: { type: String},
    imdbVotes: { type: String},
    imdbID: { type: String},
    Title: { type: String}
}, { timestamps: true });

movieDetailsSchema.plugin(random);
var MovieDetails = mongoose.model('movie_details', movieDetailsSchema);

module.exports = MovieDetails;
