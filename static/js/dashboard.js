//Reads content from webpage
function read(url, parameters = null)
{
    //Create a new http request
    var request = new XMLHttpRequest();
    var requestText = "";

    //Configure for GET request
    request.open('GET', url, false);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    //Send the request
    request.send(parameters);

    //And handle the response
    if(request.status == 200)
    {
        //Get the response
        requestText = request.responseText;
    }

    //Return the response
    return requestText
}

//Gets the wishlist
function getWishList(limit = 25)
{
    //Look for the wishlist
    var wishList = document.getElementById("wishlist");
    //Make sure wishlist is set
    if(wishList != null)
    {
        //Get data from wishlist page
        let wishListIds = read("/wishlist");
        //Check if the limit is < 0
        if(limit < 0)
            //Set limit to length of wishlist ids list
            limit = wishListIds.length
        //Split the wishlist by comma
        wishListIds = wishListIds.split(", ")
        
        //Now, create a list of books
        for(let idIndex = 0; (idIndex < wishListIds.length) && (idIndex < limit); idIndex++)
        {
            //Get the wishlisted book's title and author
            var bookData = read("/book?id="+wishListIds[idIndex]);
    
            //Check if the wishlist list is set
            if(wishList != null)
            {
                //Add book to wishlist
                book = JSON.parse(bookData);
                wishList.innerHTML += '<li><a href="/book?id=' + book["id"] + '">' + book["title"] + " by " + book["author"] + "</a></li>";   
            }
        }
    }
}

//Gets the books
function getBooks(limit = 25)
{
    //Look for books list
    var booksList = document.getElementById("books");
    //Get all books
    var books = read("/book?id=-1");
    books = JSON.parse(books);

    //Check if books list is set
    if(booksList != null)
    {
        //Go through all books within limit
        for(var index = 0; (index < books.length) && (index < limit); index++)
        {
            //Add book to books list
            var book = books[index];
            booksList.innerHTML += '<li><a href="/description?book_id=' + book["id"] + '">' + book["title"] + ' by ' + book["author"] + '</a></li>';
        }
    }
}

//On load, initialize the wishlist and books list
document.onload = new function()
{

    //Page is loaded, get the wishlist
    getWishList();
    getBooks();
};