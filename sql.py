# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 01:25:34 2020

@author: Amin
"""
import sqlalchemy, csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL="postgres://tleawrbbfikrmy:65ae335baa32a9403c3b8e31b1be8c1d99fb3a181220e88c5f84771c2c99a86d@ec2-54-197-48-79.compute-1.amazonaws.com:5432/d4pcmc1o4ff5ha"

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

#db.execute("INSERT INTO USERS (usname, pass) VALUES ('Amin', 14)")
db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader: # loop gives each column a name
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year":year})
    print(f"Added book with ISBN {isbn} entiteled as {title} writen by {author} in {year}.")
db.excecute("CREATE TABLE comments (id SERIAL PRIMARY KEY, cm VARCHAR NOT NULL, user_id INTEGER REFRENCES users, book_id INTEGER REFRENCES books)")
db.commit()
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #1',3,45);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #2',3,48);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #3',3,46);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #41',3,50);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #51',3,85);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #19',3,32);
#INSERT INTO comments (cm, user_id, book_id) VALUES ('Hello #12',3,14);                    