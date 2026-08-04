from . import db
from datetime import datetime
from zoneinfo import ZoneInfo
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )

class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )
    category = db.relationship(
        "Category",
        backref="questions"
    )

    difficulty = db.Column(db.String(20), nullable=False)

    question = db.Column(db.Text, nullable=False)

    option1 = db.Column(db.String(255), nullable=False)

    option2 = db.Column(db.String(255), nullable=False)

    option3 = db.Column(db.String(255), nullable=False)

    option4 = db.Column(db.String(255), nullable=False)

    correct_answer = db.Column(db.String(255), nullable=False)

class Result(db.Model):

    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )   

    score = db.Column(db.Integer, nullable=False)

    total_questions = db.Column(db.Integer, nullable=False)

    date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata"))
    )
    

    user = db.relationship("User", backref="results")

    category = db.relationship("Category", backref="results")

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    category_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )
