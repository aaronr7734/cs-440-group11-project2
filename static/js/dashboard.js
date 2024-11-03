//Reads content from webpage
function read(url, parameters = null) {
  //Create a new http request
  var request = new XMLHttpRequest();
  var requestText = "";

  //Configure for GET request
  request.open("GET", url, false);
  request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  //Send the request
  request.send(parameters);

  //And handle the response
  if (request.status == 200) {
    //Get the response
    requestText = request.responseText;
  }

  //Return the response
  return requestText;
}

//Gets the wishlist
function getWishList(limit = 25) {
  //Look for the wishlist
  var wishList = document.getElementById("wishlist");
  //Make sure wishlist is set
  if (wishList != null) {
    //Get data from wishlist page
    let wishListIds = read("/wishlist");
    if (!wishListIds) {
      return;
    }

    //Check if the limit is < 0
    if (limit < 0) {
      //Set limit to length of wishlist ids list
      limit = wishListIds.length;
    }

    //Split the wishlist by comma
    wishListIds = wishListIds.split(", ").filter((id) => id.length > 0);

    //Now, create a list of books
    for (
      let idIndex = 0;
      idIndex < wishListIds.length && idIndex < limit;
      idIndex++
    ) {
      //Get the wishlisted book's title and author
      var bookData = read("/book?id=" + wishListIds[idIndex]);

      //Check if we got valid book data
      if (bookData && bookData !== "No book found") {
        try {
          //Convert response to JSON and get data
          var response = JSON.parse(bookData);
          var book = response.data; // Extract from data property

          //Add book to wishlist
          wishList.innerHTML +=
            '<li><a href="/description?book_id=' +
            book.id +
            '">' +
            book.title +
            " by " +
            book.author +
            "</a></li>";
        } catch (e) {
          console.log("Error parsing book data:", e);
        }
      }
    }
  }
}

//Gets the books
function getBooks(limit = 25) {
  //Look for books list
  var booksList = document.getElementById("books");
  //Get all books
  var booksData = read("/book?id=-1");

  //Check if books list is set and we got valid data
  if (booksList != null && booksData) {
    try {
      var response = JSON.parse(booksData);
      var books = response.data; // Extract from data property
      if (books && Array.isArray(books)) {
        // Make sure books is an array
        //Go through all books within limit
        for (var index = 0; index < books.length && index < limit; index++) {
          //Add book to books list
          var book = books[index];
          booksList.innerHTML +=
            '<li><a href="/description?book_id=' +
            book.id +
            '">' +
            book.title +
            " by " +
            book.author +
            "</a></li>";
        }
      } else {
        console.log("No books found or invalid books data");
      }
    } catch (e) {
      console.log("Error parsing books data:", e);
    }
  }
}
//On load, initialize the wishlist and books list
window.onload = function () {
  //Page is loaded, get the wishlist
  getWishList();
  getBooks();
};
