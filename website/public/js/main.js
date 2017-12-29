$(document).ready(function() {

    // get form
    var form = $(document).find("form");

    var csrf = form.find('input[name="_csrf"]').val();
    var movie_id = form.find('input[name="movie_id"]').val();

    // append onclick to all the stars
    var stars = form.find('input.star');

    stars.on("click", function() {
        var rating = parseInt(this.id.replace("stars-rating-", ""));
        $.post( "/rating", { _csrf: csrf, rating: rating, movie_id: movie_id} );
    });
});