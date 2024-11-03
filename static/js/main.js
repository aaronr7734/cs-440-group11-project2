// Utility Functions
function read(url, parameters = null) {
  const request = new XMLHttpRequest();
  request.open("GET", url, false);
  request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  request.send(parameters);
  return request.status === 200 ? request.responseText : "";
}

function get(parameter) {
  const query = window.location.search.substring(1);
  const parameters = query.split("&");
  for (const param of parameters) {
    const [key, value] = param.split("=");
    if (key === parameter) {
      return value;
    }
  }
  return null;
}

async function sendPost(url, keys, values) {
  if (keys.length !== values.length) {
    console.error("sendPost(): size mismatch between keys and values.");
    return;
  }

  const data = new FormData();
  keys.forEach((key, index) => {
    data.append(key, values[index]);
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      body: data,
    });
    return response.text();
  } catch (error) {
    console.error("sendPost(): failed to send data:", error);
  }
}

// Book Description Functions
function loadBookDescription() {
  try {
    const bookId = get("book_id");
    if (!bookId) return;

    const bookResponse = read("/book?id=" + bookId);
    const book = JSON.parse(bookResponse);

    const title = document.getElementById("title");
    const author = document.getElementById("author");

    if (title && author) {
      title.textContent = book.title;
      author.textContent = "By " + book.author;
    }
  } catch (error) {
    console.error("Error loading book description:", error);
  }
}

// Review Functions
function showReviews() {
  const reviewsView = document.getElementById("reviews");
  if (!reviewsView || reviewsView.children.length > 0) return; // Prevent double loading

  try {
    const bookId = get("book_id");
    const reviewsData = read("/get?type=all&book_id=" + bookId);
    const reviews = JSON.parse(reviewsData);

    reviews.forEach((review) => {
      reviewsView.innerHTML += `
                <li>
                    <b>${review.review_title}, ${review.rating_score}/5</b>
                    <p>${review.review_text}</p>
                </li>`;
    });
  } catch (error) {
    console.error("Error showing reviews:", error);
  }
}

function showAverageRating() {
  try {
    const bookId = get("book_id");
    const avgRatingElement = document.getElementById("avg_rating");
    if (!avgRatingElement) return;

    const reviewsData = read("/get?type=all&book_id=" + bookId);
    const reviews = JSON.parse(reviewsData);

    if (!reviews.length) {
      avgRatingElement.textContent = "Average Rating: No ratings yet";
      return;
    }

    const average =
      reviews.reduce((sum, review) => sum + review.rating_score, 0) /
      (5 * reviews.length);
    avgRatingElement.textContent = `Average Rating: ${(average * 100).toFixed(
      1
    )}%`;
  } catch (error) {
    console.error("Error calculating average rating:", error);
  }
}

function showYourRating() {
  try {
    const bookId = get("book_id");
    const yourRatingElement = document.getElementById("your_rating");
    if (!yourRatingElement) return;

    const reviewData = read("/get?type=user&book_id=" + bookId);
    const review = JSON.parse(reviewData);

    if (review && review.rating_score) {
      const rating = (review.rating_score / 5) * 100;
      yourRatingElement.textContent = `Your Rating: ${rating.toFixed(1)}%`;
    } else {
      yourRatingElement.textContent = "Your Rating: Not rated yet";
    }
  } catch (error) {
    console.error("Error showing user rating:", error);
  }
}

// Rating Functions
function updateRating() {
  const bookId = get("book_id");
  const slider = document.getElementById("rating");
  if (!slider) return;

  slider.oninput = function () {
    sendPost(
      "/book",
      ["action", "type", "book_id", "rating"],
      ["update", "rating", bookId, this.value]
    );
  };
}

// Wishlist Functions
function makeATWFunctional() {
  const button = document.getElementById("add_wishlist");
  if (!button) return;

  button.onclick = function () {
    const bookId = get("book_id");
    eval(read("/add?type=wishlist&book_id=" + bookId));
  };
}

// Initialize everything
updateRating();

window.onload = function () {
  if (window.location.pathname === "/description") {
    loadBookDescription();
    showReviews();
    showAverageRating();
    showYourRating();
    makeATWFunctional();
  }
};
