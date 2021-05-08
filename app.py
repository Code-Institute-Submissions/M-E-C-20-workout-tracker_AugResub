import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_routines")
def get_routines():
    routines = list(mongo.db.routines.find())
    return render_template("routines.html", routines=routines)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome {},".format(
                            request.form.get("username")))
                        return redirect(
                            url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from the db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_exercise", methods=["GET", "POST"])
def add_exercise():
    if request.method == "POST":
        completed = "on" if request.form.get("completed") else "off"
        routine = {
            "exercise_name": request.form.get("exercise_name"),
            "weight": request.form.get("weight"),
            "sets": request.form.get("sets"),
            "reps": request.form.get("reps"),
            "completed": completed,
            "date_performed": request.form.get("date_performed"),
            "created_by": session["user"]
        }
        mongo.db.routines.insert_one(routine)
        flash("Routine Successfully Added")
        return redirect(url_for("get_routines"))

    exercise = mongo.db.exercise.find().sort("exercise_name", 1)
    return render_template("add_exercise.html", exercise=exercise)


@app.route("/edit_exercise/<exercise_id>", methods=["GET", "POST"])
def edit_exercise(exercise_id):
    if request.method == "POST":
        completed = "on" if request.form.get("completed") else "off"
        submit = {
            "exercise_name": request.form.get("exercise_name"),
            "weight": request.form.get("weight"),
            "sets": request.form.get("sets"),
            "reps": request.form.get("reps"),
            "completed": completed,
            "date_performed": request.form.get("date_performed"),
            "created_by": session["user"]
        }
        mongo.db.routines.update({"_id": ObjectId(exercise_id)}, submit)
        flash("Exercise Successfully Updated")

    routine = mongo.db.routines.find_one({"_id": ObjectId(exercise_id)})
    exercise = mongo.db.exercise.find().sort("exercise_name", 1)
    return render_template("edit_exercise.html", routine=routine, exercise=exercise)


@app.route("/delete_exercise/<exercise_id>")
def delete_exercise(exercise_id):
    mongo.db.routines.remove({"_id": ObjectId(exercise_id)})
    flash("Exercise Successfully Deleted")
    return redirect(url_for("get_routines"))


@app.route("/manage_exercises")
def manage_exercises():
    exercises = list(mongo.db.exercise.find().sort("exercise_name", 1))
    return render_template("exercises.html", exercises=exercises)


@app.route("/update_exercise_db", methods=["GET", "POST"])
def update_exercise_db():
    if request.method == "POST":
        exercises = {
            "exercise_name": request.form.get("exercise_name")
        }
        mongo.db.exercise.insert_one(exercises)
        flash("New Exercise Added")
        return redirect(url_for("manage_exercises"))

    return render_template("update_exercise_db.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
