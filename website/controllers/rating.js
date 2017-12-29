var Rating = require('../models/Rating');

/**
 * Post /rating
 * post movie rating
 */
exports.postRating = function(req, res) {
    // check if existing rating for the movie
    Rating.findOne({uid: req.user.uid, movie_id: req.body.movie_id}, function(err, existing_rating) {
        if (err) {
            console.log(err);
        }

        // save new rating
        if (!existing_rating) {
            // otherwise create a new one
              var rating = new Rating({
                uid: req.user.uid,
                movie_id: req.body.movie_id,
                rating: req.body.rating,
              });

            rating.save(function(err) {
              if (err) {
                return next(err);
              }
            });
        }
        // update the rating
        else {
            console.log(existing_rating)
            existing_rating.rating = req.body.rating;
            existing_rating.save();
        }

//        res.redirect('/movies');
    })

};