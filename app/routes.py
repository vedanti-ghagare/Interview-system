
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User , Category , Question, Result
from sqlalchemy.sql.expression import func
from sqlalchemy import or_
from time import time

main = Blueprint("main", __name__)

# Home Page
@main.route("/")
def home():
    return render_template("index.html")


# Register Page
@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        # Check email
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            flash("Email already exists!", "warning")
            return redirect(url_for("main.register"))

        # Check username
        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash("Username already exists!", "warning")
            return redirect(url_for("main.register"))
        user = User(
            
            email=email,
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please login.", "success")

        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("main.admin_dashboard"))

            return redirect(url_for("main.dashboard"))

        flash("Invalid Username or Password!", "danger")
        return redirect(url_for("main.login"))

    return render_template("login.html")
@main.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    results = Result.query.filter_by(
        user_id=user.id
    ).order_by(Result.date.desc()).all()

    total_results = len(results)

    highest_score = max([r.score for r in results], default=0)

    average_percentage = round(
        sum((r.score / r.total_questions) * 100 for r in results) / total_results,
        2
    ) if total_results else 0

    last_attempt = results[0].date if results else None

    return render_template(
        "dashboard.html",
        username=user.username,
        total_results=total_results,
        highest_score=highest_score,
        average_percentage=average_percentage,
        last_attempt=last_attempt
    )

@main.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("role", None)

    flash("Logged out successfully.", "info")
    return redirect(url_for("main.login"))

@main.route("/interview", methods=["GET", "POST"])
def interview():

    if "user" not in session:
        return redirect(url_for("main.login"))

    if request.method == "POST":

        category = request.form["category"]
        difficulty = request.form["difficulty"]
        question_count = request.form["question_count"]

        return redirect(
            url_for(
                "main.start_test",
                category=category,
                difficulty=difficulty,
                question_count=question_count
            )
        )

    categories = Category.query.all()

    return render_template(
        "interview.html",
        categories=categories
    )

@main.route("/results")
def results():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    results = Result.query.filter_by(
        user_id=user.id
    ).all()

    return render_template(
        "results.html",
        results=results
    )

@main.route("/profile")
def profile():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    return render_template(
        "profile.html",
        user=user
    )

@main.route("/admin")
def admin_dashboard():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        return "Access Denied!"

    return render_template("admin_dashboard.html")

@main.route("/admin/categories", methods=["GET", "POST"])
def categories():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        return "Access Denied!"

    if request.method == "POST":

        name = request.form["category"]

        existing = Category.query.filter_by(category_name=name).first()

        if existing:
            return "Category already exists!"

        category = Category(category_name=name)

        db.session.add(category)

        db.session.commit()

        return redirect(url_for("main.categories"))

    categories = Category.query.all()

    return render_template(
        "category.html",
        categories=categories
    )

@main.route("/admin/questions", methods=["GET", "POST"])
def questions():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        return "Access Denied!"

    if request.method == "POST":

        question = Question(

            category_id=request.form["category"],

            difficulty=request.form["difficulty"],

            question=request.form["question"],

            option1=request.form["option1"],

            option2=request.form["option2"],

            option3=request.form["option3"],

            option4=request.form["option4"],

            correct_answer=request.form["answer"]

        )

        db.session.add(question)

        db.session.commit()

        return redirect(url_for("main.questions"))

    categories = Category.query.all()

    return render_template(
        "question.html",
        categories=categories
    )

@main.route("/admin/view_questions")
def view_questions():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        flash("Access Denied!", "danger")
        return redirect(url_for("main.dashboard"))

    search = request.args.get("search")

    if search:

        questions = Question.query.join(Category).filter(

            or_(
                Category.category_name.ilike(f"%{search}%"),
                Question.question.ilike(f"%{search}%")
            )

        ).all()

    else:

        questions = Question.query.all()

    return render_template(
        "view_questions.html",
        questions=questions,
        search=search
    )
@main.route("/admin/edit_question/<int:id>", methods=["GET", "POST"])
def edit_question(id):

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        return "Access Denied!"

    question = Question.query.get_or_404(id)

    categories = Category.query.all()

    if request.method == "POST":

        question.category_id = request.form["category"]
        question.difficulty = request.form["difficulty"]
        question.question = request.form["question"]
        question.option1 = request.form["option1"]
        question.option2 = request.form["option2"]
        question.option3 = request.form["option3"]
        question.option4 = request.form["option4"]
        question.correct_answer = request.form["answer"]

        db.session.commit()

        return redirect(url_for("main.view_questions"))

    return render_template(
        "edit_question.html",
        question=question,
        categories=categories
    )

@main.route("/admin/delete_question/<int:id>")
def delete_question(id):

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(username=session["user"]).first()

    if user.role != "admin":
        return "Access Denied!"

    question = Question.query.get_or_404(id)

    db.session.delete(question)

    db.session.commit()

    return redirect(url_for("main.view_questions"))

@main.route("/start_test")
def start_test():

    if "user" not in session:
        return redirect(url_for("main.login"))

    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    question_count = int(request.args.get("question_count"))

    available = Question.query.filter_by(
        category_id=category,
        difficulty=difficulty
    ).count()

    if question_count > available:

        flash(
            f"Only {available} questions are available for this category and difficulty.",
            "warning"
        )

        return redirect(url_for("main.interview"))

    questions = Question.query.filter_by(
        category_id=category,
        difficulty=difficulty
    ).order_by(func.random()).limit(question_count).all()

    

    return render_template(
        "start_test.html",
        questions=questions,
        category=category
    )


@main.route("/submit_test", methods=["POST"])
def submit_test():

    if "user" not in session:
        return redirect(url_for("main.login"))

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    category = request.form["category"]

   

    score = 0
    total = 0

    review = []

    questions = Question.query.filter_by(
        category_id=category
    ).all()

    for question in questions:

        user_answer = request.form.get(str(question.id))

        if user_answer:

            total += 1

            is_correct = user_answer == question.correct_answer

            if is_correct:
                    score += 1

            review.append({
                "question": question.question,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct
            })

    result = Result(

        user_id=user.id,

        category_id=category,

        score=score,

        total_questions=total

        

    )

    db.session.add(result)

    db.session.commit()

    return render_template(
        "result.html",
        score=score,
        total=total,
        review=review
    )

@main.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            if user.role != "admin":
                flash("Access Denied! You are not an administrator.", "danger")
                return redirect(url_for("main.admin_login"))

            session["user"] = user.username
            session["role"] = "admin"
            flash("Admin Login Successful!", "success")
            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid Username or Password!", "danger")
        return redirect(url_for("main.admin_login"))

    return render_template("admin_login.html")