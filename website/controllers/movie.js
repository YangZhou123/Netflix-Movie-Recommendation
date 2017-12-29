var MovieDetails = require('../models/MovieDetails');
var Rec = require('../models/Rec');
var Rating = require('../models/Rating');

/**
* separate movie list to find top movies
*/
function separateMovieList(movie_list) {

    var organizedMovieList = {};
    var featuredMovieList = [];
    var restMovieList = [];

    var movie = {};
    for (var i=0, len=movie_list.length; i<len; i++) {
        movie = movie_list[i];

        if (movie.imdbRating && movie.Poster) {
            if (movie.Poster !== "N/A") {
                if (parseInt(movie.imdbRating) >= 7) {
                    featuredMovieList.push(movie);
                } else {
                    restMovieList.push(movie);
                }
            }
        } else {
            restMovieList.push(movie);
        }
    }

    organizedMovieList.featured = featuredMovieList;
    organizedMovieList.rest = restMovieList;

    return organizedMovieList;
}


function mostRecentRec(recs) {
    var len = recs.length;
    return recs[len-1];
}


/**
 * GET /movie
 * Movie home page
 */
exports.getMovieMain = function(req, res) {
    MovieDetails.findRandom({}, {}, {limit: 100}, function(err, movie_list) {
      if (!err) {
        // find the highest rank in those movies
        var organizedMovieList = separateMovieList(movie_list)

        // find personal recommendation for the current user
        var currUserId = req.user.uid;

        Rec.find({uid: currUserId}, function(err, recs) {
            if (recs.length === 0) {
                // return empty list
                organizedMovieList.rec = [];

                // display the list
                res.render('movie_main', {
                    title: 'Movies',
                    rec: organizedMovieList.rec,
                    movie_list: organizedMovieList.featured,
                     rest: organizedMovieList.rest
                });
            } else {
                // find recent user recommendation
                recentRec = mostRecentRec(recs)
                MovieDetails.find({
                    'id': { $in: recentRec.mid}
                }, function(err, personalRecs){
                     organizedMovieList.rec = personalRecs;

                     // display the list
                     res.render('movie_main', {
                        title: 'Movies',
                        rec: organizedMovieList.rec,
                        movie_list: organizedMovieList.featured,
                        rest: organizedMovieList.rest
                     });
                });
            }
        })
      }
    });
};


/**
 * GET /movie
 * Movie home page
 */
exports.getSingleMovie = function(req, res) {
    MovieDetails.findOne({id:req.params.id}).exec(function(errors, movie) {
          if (errors) {
            console.log(errors);
          }

          // find user's previous rating
          var currUserId = req.user.uid;
          var movieId = movie.id;

          Rating.findOne({uid: currUserId, movie_id: movieId}, function(errors, existingRating) {
            var rating = 0;
            if (existingRating !== null) {
                rating = existingRating.rating;
            }

            res.render('movie_single', {
                title: 'Movie',
                movie: movie,
                rating: rating
             });
          })


    });
};

/**
 * GET /movie/trending
 * trending movies
 */
exports.getMovieTrending = function(req, res) {
    MovieDetails.find({}).limit(5).exec(function(errors, movie_list) {
      if (errors) {
        req.flash('errors', errors);
        return res.redirect('/movie');
      }

      res.json(movie_list);
    })
};