//Gets variable value from URL
function get(parameter) {
  //Get parameter value from url
  var query = window.location.search.substring(1);
  var parameters = query.split("&");
  for (var index = 0; index < parameters.length; index++) {
    var pair = parameters[index].split("=");
    if (pair[0] == parameter) {
      //Return the value of this parameter
      return pair[1];
    }
  }
}

//Sends form data to a page via POST
async function sendPost(url, keys, values) {
  //Create form data
  const data = new FormData();

  //Check if there is a size mismatch
  if (keys.length != values.length) {
    console.log("sendPost(): size mismatch between keys and values.");
  } else {
    //Add all keys and values to form data
    for (var index = 0; index < keys.length; index++) {
      //Add current key and value to form data
      data.append(keys[index], values[index]);
    }
  }

  //Try to send the data
  try {
    //Send the data
    const response = await fetch(url, {
      method: "POST",
      body: data,
    });
    //And get the response
    return response.text();
  } catch (e) {
    console.log("sendData(): failed to send data.");
  }
}

//Updates rating based on slider value
function updateRating() {
  //Get the book id and slider
  var book_id = get("book_id");
  var slider = document.getElementById("rating");
  if (!slider) return; // Exit if we're not on a page with the rating slider

  var sliderValue = 0;
  var submit = document.getElementById("submit");

  var reviewTitle = document.getElementById("review_title").innerText;
  var reviewText = document.getElementById("review_text").innerText;

  //When the slider is moved, update the rating in our database
  slider.oninput = function () {
    //Send a post updating rating
    sliderValue = this.value;
    sendPost(
      "/book",
      ["action", "type", "book_id", "rating"],
      ["update", "rating", book_id, sliderValue]
    );
  };
}

function loadBookDescription() {
  var book_id = get("book_id");
  var bookResponse = read("/book?id=" + book_id);

  try {
    var response = JSON.parse(bookResponse);
    var book = response.data;

    var title = document.getElementById("title");
    var author = document.getElementById("author");

    if (title && author) {
      title.textContent = book.title;
      author.textContent = "By " + book.author;
    }
  } catch (e) {
    console.error("Error loading book description:", e);
  }
}

//Shows all reviews
function showReviews() {
  var reviewsView = document.getElementById("reviews");
  if (reviewsView && reviewsView.children.length === 0) {
    // Only load if no reviews yet
    var book_id = get("book_id");
    if (reviewsView != null) {
      var reviewsData = read("/get?type=all&book_id=" + book_id);
      if (reviewsData) {
        var response = JSON.parse(reviewsData);
        var reviews = response.data;
        for (var index = 0; index < reviews.length; index++) {
          var review = reviews[index];
          var reviewTitle = review.review_title;
          var reviewText = review.review_text;
          var rating = review.rating_score;

          reviewsView.innerHTML +=
            "<li><b>" + reviewTitle + ", " + rating + "/5</b>";
          reviewsView.innerHTML += "<p>" + reviewText + "</p></li>";
        }
      }
    }
  }
}

//Show average rating for a book
function showAverageRating() {
  //Get all reviews
  var bookId = get("book_id");
  var avgRating = document.getElementById("avg_rating");
  var average = 0;
  if (avgRating != null) {
    //Get all reviews with associated book id
    var reviewsData = read("/get?type=all&book_id=" + bookId);
    if (reviewsData) {
      var response = JSON.parse(reviewsData);
      var reviews = response.data; // Extract from data property
      if (reviews && reviews.length > 0) {
        //Determine the average rating
        for (var index = 0; index < reviews.length; index++) {
          //Get current review
          var review = reviews[index];
          //And use it to determine average
          average += review.rating_score;
        }

        //Now convert it to an actual average
        average = average / (5 * reviews.length);

        //And update the current average rating
        avgRating.innerText =
          "Average Rating: " + (average * 100).toFixed(1) + "%";
      } else {
        avgRating.innerText = "Average Rating: No ratings yet";
      }
    }
  }
}

//Show your rating
function showYourRating() {
  //Show your rating
  var bookId = get("book_id");
  var yourRating = document.getElementById("your_rating");
  if (yourRating != null) {
    //Get user's review
    var reviewData = read("/get?type=user&book_id=" + bookId);
    if (reviewData) {
      var response = JSON.parse(reviewData);
      if (response.data) {
        // Extract from data property
        var rating = (response.data.rating_score / 5) * 100;
        //And get the rating score
        yourRating.innerText = "Your Rating: " + rating.toFixed(1) + "%";
      } else {
        yourRating.innerText = "Your Rating: Not rated yet";
      }
    }
  }
}

//Implements add to wishlist button
function makeATWFunctional() {
  //Get the add to wishlist button
  var button = document.getElementById("add_wishlist");
  if (!button) return; // Exit if we're not on a page with the wishlist button

  //When its clicked, add the book to current wishlist
  button.onclick = function () {
    //Get the book ID
    var bookId = get("book_id");
    //And try to add it to wishlist
    eval(read("/add?type=wishlist&book_id=" + bookId));
  };
}

//Start updating rating
updateRating();

window.onload = function () {
  if (window.location.pathname === "/description") {
    loadBookDescription();
  }
  showReviews();
  showAverageRating();
  showYourRating();
  makeATWFunctional();
};
