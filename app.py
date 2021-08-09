import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/welcome_page")
def welcome_page():
    if "user" in session:
        return redirect(url_for(
                "workout_history", username=session["user"]))
    else:
        return render_template("index.html")


@app.route("/get_workouts")
def get_workouts():
    if "user" not in session:
        flash("You need to log in to do that!")

        return redirect(url_for("login"))
    else:
        # retrieve the list of planned workouts and sort them by date
        workouts = list(mongo.db.routines.find().sort("_id", 1))
        return render_template("workout_planner.html", workouts=workouts)


@app.route("/search", methods=["GET", "POST"])
def search():
    # search the db for exercise name
    query = request.form.get("query")
    workouts = list(mongo.db.routines.find({"$text": {"$search": query}}))
    return render_template("workout_planner.html", workouts=workouts)


@app.route("/search_completed_workouts", methods=["GET", "POST"])
def search_completed_workouts():
    existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})
    if existing_user:
        # search the db for exercise name
        locate = request.form.get("locate")
        workouts = list(mongo.db.completed_workouts.find(
            {"$text": {"$search": locate}}))
        return render_template("workout_history.html", workouts=workouts)
    else:
        flash("You need to be logged in!")
        return redirect(url_for("login"))


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

        # passwords not matching
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
        return redirect(url_for("workout_history", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for(
                "workout_history", username=session["user"]))
    elif request.method != "POST":
        return render_template("login.html")
    else:
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}".format(
                    request.form.get("username")))
                return redirect(
                    url_for(
                        "workout_history", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/workout_history/<username>", methods=["GET", "POST"])
def workout_history(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if username:
        # retrieve the list of completed workouts and sort them by date
        workouts = list(mongo.db.completed_workouts.find())
        sorted_workouts = sorted(
            workouts, key=lambda x: datetime.strptime(
                x["due_date"], "%d %B, %Y"), reverse=False)
        return render_template(
            "workout_history.html",
            username=username,
            workouts=sorted_workouts
            )
    else:
        flash("You need to be logged in!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if "user" not in session:
        flash("You need to log in to do that!")

        return redirect(url_for("login"))
    # retrieve workout data from form and send it to the db
    elif request.method == "POST":
        workout = {
            "exercise_name": request.form.get("exercise_name"),
            "weight": request.form.get("weight"),
            "sets": request.form.get("sets"),
            "reps": request.form.get("reps"),
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.routines.insert_one(workout)
        flash("Workout Added")
        return redirect(url_for("get_workouts"))

    exercise = mongo.db.exercise.find().sort("exercise_name", 1)
    return render_template("add_workout.html", exercise=exercise)


@app.route("/edit_workout/<workout_id>", methods=["GET", "POST"])
def edit_workout(workout_id):
    if request.method == "POST":
        submit = {
            "exercise_name": request.form.get("exercise_name"),
            "weight": request.form.get("weight"),
            "sets": request.form.get("sets"),
            "reps": request.form.get("reps"),
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mongo.db.routines.update({"_id": ObjectId(workout_id)}, submit)
        flash("Workout Updated")

    workout = mongo.db.routines.find_one({"_id": ObjectId(workout_id)})
    exercise = mongo.db.exercise.find().sort("exercise_name", 1)
    return render_template(
        "edit_workout.html", workout=workout, exercise=exercise)


@app.route("/delete_planned_workout/<workout_id>")
def delete_planned_workout(workout_id):
    # find workout and remove from db
    mongo.db.routines.remove({"_id": ObjectId(workout_id)})
    flash("Workout Deleted")
    return redirect(url_for("get_workouts"))


@app.route("/delete_completed_workout/<workout_id>")
def delete_completed_workout(workout_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # find completed workout and remove from the db
    mongo.db.completed_workouts.remove({"_id": ObjectId(workout_id)})
    flash("Workout Deleted")
    return redirect(url_for("workout_history", username=username))


@app.route("/complete_workout/<workout_id>", methods=["GET", "POST"])
def complete_workout(workout_id):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # update completed workouts and remove from planned workouts in the db
    if request.method == "POST":
        workout = {
            "exercise_name": request.form.get("exercise_name"),
            "weight": request.form.get("weight"),
            "sets": request.form.get("sets"),
            "reps": request.form.get("reps"),
            "due_date": request.form.get("due_date"),
            "workout_notes": request.form.get("workout_notes"),
            "created_by": session["user"]
        }
        mongo.db.completed_workouts.insert_one(workout)
        mongo.db.routines.remove({"_id": ObjectId(workout_id)})
        flash("Workout Added")
        return redirect(url_for("workout_history", username=username))

    workout = mongo.db.routines.find_one({"_id": ObjectId(workout_id)})
    exercise = mongo.db.exercise.find().sort("exercise_name", 1)
    return render_template(
        "complete_workout.html", exercise=exercise,
        workout=workout, username=username)


@app.route("/manage_exercises")
def manage_exercises():
    # prevent unauthorised users from accessing the exercise db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username != "admin":
        flash("You do not have admin permissions!")
        return redirect(url_for("get_workouts"))
    else:
        exercises = list(mongo.db.exercise.find().sort("exercise_name", 1))
        return render_template("exercises.html", exercises=exercises)


@app.route("/update_exercise_db", methods=["GET", "POST"])
def update_exercise_db():
    # prevent unauthorised users from accessing the exercise db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username != "admin":
        flash("You do not have admin permissions!")
        return redirect(url_for("get_workouts"))
    # update the db with new exercise
    elif request.method == "POST":
        exercises = {
            "exercise_name": request.form.get("exercise_name")
        }
        mongo.db.exercise.insert_one(exercises)
        flash("New Exercise Added")
        return redirect(url_for("manage_exercises"))

    return render_template("update_exercise_db.html")


@app.route("/edit_exercise_db/<exercise_id>", methods=["GET", "POST"])
def edit_exercise_db(exercise_id):
    # prevent unauthorised users from accessing the exercise db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username != "admin":
        flash("You do not have admin permissions!")
        return redirect(url_for("get_workouts"))
    # retrieve exercise from the db and update
    elif request.method == "POST":
        submit = {
            "exercise_name": request.form.get("exercise_name")
        }
        mongo.db.exercise.update({"_id": ObjectId(exercise_id)}, submit)
        flash("Exercise Updated")
        return redirect(url_for("manage_exercises"))

    exercises = mongo.db.exercise.find_one({"_id": ObjectId(exercise_id)})
    return render_template("edit_exercise_db.html", exercises=exercises)


@app.route("/delete_exercise_db/<exercise_id>")
def delete_exercise_db(exercise_id):
    # prevent unauthorised users from accessing the exercise db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username != "admin":
        flash("You do not have admin permissions!")
        return redirect(url_for("get_workouts"))
    else:
        # remove exercise from the db
        mongo.db.exercise.remove({"_id": ObjectId(exercise_id)})
        flash("Exercise Deleted")
        return redirect(url_for("manage_exercises"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
