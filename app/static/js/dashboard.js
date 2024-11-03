function getWishList(limit = 25) {
  const wishList = document.getElementById("wishlist");
  if (!wishList) return;

  try {
    // Get data from wishlist page
    let wishListIds = read("/wishlist");
    if (!wishListIds) return;

    // Process wishlist IDs
    wishListIds = wishListIds.split(", ").filter((id) => id.length > 0);

    // Adjust limit if needed
    if (limit < 0) {
      limit = wishListIds.length;
    }

    // Create list of books
    for (
      let idIndex = 0;
      idIndex < wishListIds.length && idIndex < limit;
      idIndex++
    ) {
      const bookData = read("/book?id=" + wishListIds[idIndex]);

      if (bookData && bookData !== "No book found") {
        try {
          const book = JSON.parse(bookData);
          wishList.innerHTML += `
                        <li>
                            <a href="/description?book_id=${book.id}">
                                ${book.title} by ${book.author}
                            </a>
                        </li>`;
        } catch (e) {
          console.error("Error parsing book data:", e);
        }
      }
    }
  } catch (error) {
    console.error("Error loading wishlist:", error);
  }
}

function getBooks(limit = 25) {
  const booksList = document.getElementById("books");
  if (!booksList) return;

  try {
    const booksData = read("/book?id=-1");
    if (!booksData) return;

    const books = JSON.parse(booksData);
    if (!Array.isArray(books)) {
      console.error("Invalid books data received");
      return;
    }

    for (let index = 0; index < books.length && index < limit; index++) {
      const book = books[index];
      booksList.innerHTML += `
                <li>
                    <a href="/description?book_id=${book.id}">
                        ${book.title} by ${book.author}
                    </a>
                </li>`;
    }
  } catch (error) {
    console.error("Error loading books:", error);
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  const path = window.location.pathname;
  if (path === "/dashboard") {
    getWishList();
  } else if (path === "/books") {
    getBooks();
  }
});
