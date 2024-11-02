
//Gets variable value from URL
function get(parameter)
{
    //Get parameter value from url
    var query = window.location.search.substring(1);
    var parameters = query.split("&");
    for(var index = 0; index < parameters.length; index++)
    {
        var pair = parameters[index].split("=");
        if(pair[0] == parameter)
        {
            //Return the value of this parameter
            return pair[1];
        }
    }
}

//Sends form data to a page via POST
async function sendPost(url, keys, values)
{
    //Create form data
    const data = new FormData();

    //Check if there is a size mismatch
    if(keys.length != values.length)
    {
        console.log("sendPost(): size mismatch between keys and values.");
    }
    else
    {
        //Add all keys and values to form data
        for(var index = 0; index < keys.length; index++)
        {
            //Add current key and value to form data
            data.append(keys[index], values[index]);
        }
    }

    //Try to send the data
    try
    {
        //Send the data
        const response = await fetch(url, {
            method: "POST",
            body: data
        });
        //And get the response
        return response.text()
    } catch (e)
    {
        console.log("sendData(): failed to send data.");
    }
}

//Updates rating based on slider value
function updateRating()
{
    //Get the book id and slider
    var book_id = get("book_id");
    var slider = document.getElementById("rating");
    var sliderValue = 0;
    var submit = document.getElementById("submit");

    var reviewTitle = document.getElementById("review_title").innerText;
    var reviewText = document.getElementById("review_text").innerText;

    //When the slider is moved, update the rating in our database
    slider.oninput = function()
    {
        //Send a post updating rating
        sliderValue = this.value;
        sendPost("/book", ["action", "type", "book_id", "rating"], ["update", "rating", book_id, sliderValue]);
    }
}

//Shows all reviews
function showReviews()
{
    //Get all reviews
    var book_id = get("book_id");
    var reviewsView = document.getElementById("reviews");
    if(reviewsView != null)
    {
        //Read all reviews
        var reviews = JSON.parse(read("/get?type=all&book_id=" + book_id));
        console.log(reviews);
        //Show all reviews
        for(var index = 0; index < reviews.length; index++)
        {
            //Get current review
            var review = reviews[index];
            var reviewTitle = review["review_title"];
            var reviewText = review["review_text"];
            var rating = review["rating_score"];

            //And add it to reviews list
            reviewsView.innerHTML += "<li><b>" + reviewTitle + ", " + rating + "/5</b>";
            reviewsView.innerHTML += "<p>" + reviewText + "</p></li>";
        }
    }
}

//Show average rating for a book
function showAverageRating()
{
    //Get all reviews
    var bookId = get("book_id");
    var avgRating = document.getElementById("avg_rating");
    var average = 0
    if(avgRating != null)
    {
        //Get all reviews with associated book id
        var reviews = JSON.parse(read("/get?type=all&book_id=" + bookId));
        //Determine the average rating
        for(var index = 0; index < reviews.length; index++)
        {
            //Get current review
            var review = reviews[index];
            //And use it to determine average
            average += review["rating_score"];
        }

        //Now convert it to an actual average
        average = average / (5 * reviews.length);

        //And update the current average rating
        avgRating.innerText = "Average Rating: " + (average * 100) + "%";
    }
}

//Show your rating
function showYourRating()
{
    //Show your rating
    var bookId = get("book_id");
    var yourRating = document.getElementById("your_rating");
    if(yourRating != null)
    {
        //Get user's review
        var review = JSON.parse(read("/get?type=user&book_id=" + bookId));
        var rating = ((review["rating_score"]) / 5) * 100;
        //And get the rating score
        yourRating.innerText = "Your Rating: " + rating + "%";
    }
}

//Implements add to wishlist button
function makeATWFunctional()
{
    //Get the add to wishlist button
    var button = document.getElementById("add_wishlist");
    //When its clicked, add the book to current wishlist
    button.onclick = function()
    {
        //Get the book ID
        var bookId = get("book_id");
        //And try to add it to wishlist
        eval(read("/add?type=wishlist&book_id=" + bookId));
    }
}

//Start updating rating
updateRating();

//And show the reviews
showReviews();

window.onload = function()
{
    showReviews();
    showAverageRating();
    showYourRating();
    makeATWFunctional();
}