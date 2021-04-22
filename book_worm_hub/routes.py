import requests

from flask import render_template, redirect, flash, url_for, request, jsonify, session
from book_worm_hub import app, db, bcrypt
from book_worm_hub.forms import RegistrationForm, LoginForm
from db import addUser, checkField, getData
from flask_login import login_user, current_user, logout_user, login_required 


@app.route("/",  methods=["POST", "GET"])
def index():
    # if current_user.is_authenticated:
    #     return redirect(url_for('account'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Form is valid")
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        form.password.data = hashedPassword
        user = addUser(form.email.data, form.password.data)
        flash(f'Account successfully created you can now login into your account', 'success')
        return redirect(url_for('login'))
    print("not valid upon submission")
    return render_template('index.html', form=form)

# @app.route("/register")
# def index():
#     return "Project One: TODO"

@app.route("/login", methods=["POST", "GET"])
def login():   
    form = LoginForm()
    if form.validate_on_submit():
        user = checkField("users", "email", form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            return render_template('account.html', username=form.email.data)
    return render_template('login.html', title="Login", form=LoginForm())
@app.route("/logout")
def logout():
    try:
        session.pop("user_email")
    except KeyError:
        flash(f'Please login first', 'warning')
        return render_template("login.html")
    return render_template("index.html", status="Loggedout")

@app.route("/search", methods=["GET", "POST"])
def account():   
    if request.method == "POST":
        # # Checking if the user is present, if not present show error message and redirect to /register
        # email = request.form.get("Email")
        # user = db.execute("SELECT id, password FROM users WHERE email= :email", {"email": email}).fetchone()
        # if user is None:
        #     flash(f'Please register first', 'warning')
        #     return redirect(url_for('index'))

        # password = request.form.get("Password")
        # if not check_password_hash(user.password, password):
        #     flash(f'Your password doesnt match', 'danger')
        #     return redirect(url_for('login'))
        return redirect(url_for('index'))
# Page to show books as per search result
@app.route("/booklist", methods=["POST"])
def booklist():
    print("here")
    book_column = request.form.get("book_column")
    query = request.form.get("query")

    if book_column == "year":
        book_list = db.execute("SELECT * FROM books WHERE year = :query", {"query": query}).fetchall()
    else:
        book_list = db.execute("SELECT * FROM books WHERE UPPER(" + book_column + ") = :query ORDER BY title",
                               {"query": query.upper()}).fetchall()

    # Is whole of the info i.e. ISBN, title matches...
    if len(book_list):
        return render_template("book.html", book=book_list)

    elif book_column != "year":
        error_message = "We couldn't find the books you searched for."
        book_list = db.execute("SELECT * FROM books WHERE UPPER(" + book_column + ") LIKE :query ORDER BY title",
                               {"query": "%" + query.upper() + "%"}).fetchall()
        if not len(book_list):
            return render_template("error.html", error_message=error_message)
        message = "You might be searching for:"
        return render_template("bookpage.html", error_message=error_message, book_list=book_list, message=message,
                               user_email=session["user_email"])
    else:
        return render_template("error.html", error_message="We didn't find any book with the year you typed."
                                                          " Please check for errors and try again.")
@app.route("/detail/<int:book_id>", methods=["GET", "POST"])
def detail(book_id):
    if "user_email" not in session:
        return render_template("login.html", error_message="Please Login First", work="Login")

    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", error_message="We got an invalid book id"
                                                           ". Please check for the errors and try again.")

    # When review if submitted for the book.
    if request.method == "POST":
        user_id = session["user_id"]
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        if db.execute("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                      {"user_id": user_id, "book_id": book_id}).fetchone() is None:
            db.execute(
                "INSERT INTO reviews (user_id, book_id, rating, comment) VALUES (:user_id, :book_id, :rating, :comment)",
                {"book_id": book.id, "user_id": user_id, "rating": rating, "comment": comment})
        else:
            db.execute(
                "UPDATE reviews SET comment = :comment, rating = :rating WHERE user_id = :user_id AND book_id = :book_id",
                {"comment": comment, "rating": rating, "user_id": user_id, "book_id": book_id})
        db.commit()

    """Goodreads API"""
    # Processing the json data
    
    key = "AIzaSyB9P2W2FF9_0gnIo6An7pYtLkdWxcTsTvM"
    isbn = book.isbn
    bookdata = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={key}")
    res = bookdata.json()
    for item in res.get('items'):
        ratings_count = item.get('volumeInfo').get('ratingsCount')
        average_rating = item.get('volumeInfo').get('averageRating')
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", ratings_count)
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    users = []
    for review in reviews:
        email = db.execute("SELECT email FROM users WHERE id = :user_id", {"user_id": review.user_id}).fetchone().email
        users.append((email, review))

    return render_template("detail.html", book=book, users=users,
                           ratings_count=ratings_count, average_rating=average_rating, user_email=session["user_email"])


# Page for the website's API
@app.route("/api/<ISBN>", methods=["GET"])
def api(ISBN):
    book = db.execute("SELECT * FROM books WHERE isbn = :ISBN", {"ISBN": ISBN}).fetchone()
    if book is None:
        return render_template("error.html", error_message="We got an invalid ISBN. "
                                                           "Please check for the errors and try again.")
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchall()
    count = 0
    rating = 0
    for review in reviews:
        count += 1
        rating += review.rating
    if count:
        average_rating = rating / count
    else:
        average_rating = 0

    return jsonify(
        title=book.title,
        author=book.author,
        year=book.year,
        isbn=book.isbn,
        review_count=count,
        average_score=average_rating
    )
