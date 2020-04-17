import requests
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
DATABASE_URL="postgres://cldgwdenszyeox:aa532678a30f2c905943fd4490d017914bc84d1f549b44e9e6ced39089f8d2a9@ec2-54-165-36-134.compute-1.amazonaws.com:5432/d5hu4bigkc2a2p"


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/register", methods=["POST"])
def register():
    name=request.form.get("name")
    passw=request.form.get("password")
    db.execute("INSERT INTO users (usname,pass) VALUES (:usname,:pass)", {"usname":name, "pass":passw})
    db.commit()
    return render_template("hello.html",name=name)
    return redirect(url_for('login'))
@app.route("/login", methods=["POST"])
def login():
    name=request.form.get("name")
    passw=request.form.get("password")
    lg=db.execute("SELECT * FROM users WHERE (usname=:usname) AND (pass=:pass)", {"usname":name, "pass":passw}).fetchall()
    if not lg:
        return render_template("hello.html",name='No user found')
    else:
        session['name']=lg[0].usname
        session['user_id']=lg[0].id
        user_id=session['user_id']
        session['cmm']=db.execute("SELECT cm, title FROM comments JOIN books ON books.id=book_id WHERE user_id=:user_id", {"user_id":user_id}).fetchall()
        return redirect(url_for('userpage'))

@app.route("/userpage")
def userpage():
    name=session['name']
    cmm=session['cmm']
    return render_template("profile.html",name=name,cmm=cmm)
@app.route("/results", methods=["POST"])
def results():
    ISBN=request.form.get("ISBN")
    title=request.form.get("title")
    author=request.form.get("author")
    session['res']=db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author", {"isbn":f"%{ISBN}%", "title":f"%{title}%", "author":f"%{author}%"}).fetchall()
    return render_template("results.html",res=session['res'])
@app.route("/results/<name>")
def alikale(name):
    idd=name[2:]
    if not session['user_id']:
        return render_template("hello.html",name=name)
    else:
        res=session['res']
        session['cmbook']=db.execute("SELECT cm, usname FROM comments JOIN users ON users.id= user_id WHERE book_id=:book_id", {"book_id":res[int(idd)].id}).fetchall()
        cmbook=session['cmbook']
        isbn=res[int(idd)].isbn
        resapi = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Y5fYXr4UjSLiWiSWUcdQQ", "isbns": isbn })
        if resapi.status_code == 404:
            resapi= "No rating"
        else:
             resapi=resapi.json()
             resapi=resapi["books"][0]["average_rating"]
        return render_template("searchresults.html",author=res[int(idd)].author, title=res[int(idd)].title, isbn=res[int(idd)].isbn, year=res[int(idd)].year, cmbook=cmbook, bookid=res[int(idd)].id, resapi=resapi)
    
@app.route("/submiting", methods=["POST"])
def submiting():
    cm=request.form.get("comment")
    bookid=request.form.get("bookid")
    db.execute("INSERT INTO comments (cm, user_id, book_id) VALUES (:cm, :user_id, :book_id)",{"cm": cm, "user_id": session['user_id'], "book_id": bookid})
    db.commit()
    return "submited!"
@app.route("/logout")
def logout():
    session.pop('res',None)
    session.pop('cmm',None)
    session.pop('name',None)
    session.pop('user_id',None)
    print('You were logged out')
    return (redirect(url_for('index')))
@app.route("/api/<name>")
def api(name):
    bookapi=db.execute("SELECT title, author, isbn, year, count(*) FROM books JOIN comments ON comments.book_id=books.id WHERE books.isbn= :isb GROUP BY books.title, books.author, books.isbn, books.year", {"isb":name}).fetchall()
    return jsonify({
                    "title": bookapi[0].title,
                    "author": bookapi[0].author,
                    "year": bookapi[0].year,
                    "isbn": bookapi[0].isbn,
                    "review_count": bookapi[0].count,
                    "average_score": 5.0
                    })