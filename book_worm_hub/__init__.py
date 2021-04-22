import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
# app.config['DATABASE_URL'] = "postgres://uklopmtmcykcay:259fb092bc5a29c619a910f3b3ddbfa653d9d0b482f5a9f19406d524d75ab5d5@ec2-34-225-103-117.compute-1.amazonaws.com:5432/d8ig99lvjck7it"
app.config['SECRET_KEY'] = 'f38562b51305c4a9e68ba32d2f7ca69'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
bcrypt = Bcrypt(app)
from book_worm_hub import routes