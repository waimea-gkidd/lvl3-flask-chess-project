#===========================================================
# CHESS PROJECT
# By Gideon Kidd
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Show the Teams Tournament info
#-----------------------------------------------------------
@app.get("/")
@login_required
def show_home():
    # day/location still hardcoded - not stored in the DB
    tt_day = "Wed"
    tt_location = "Tahunanui Community Hub"

    with connect_db() as db:
        sql = """
            SELECT semester_id, phase_id
            FROM tournaments
            ORDER BY id DESC
            LIMIT 1
        """
        params = ()
        tournament = db.execute(sql, params).fetchone()

    if tournament:
        tt_semester = tournament["semester_id"]
        tt_phase = tournament["phase_id"]
    else:
        tt_semester = None
        tt_phase = None

    return render_template(
        "pages/home.jinja",
        tt_day=tt_day,
        tt_location=tt_location,
        tt_semester=tt_semester,
        tt_phase=tt_phase,
    )


#-----------------------------------------------------------
# Teams Tournament page - placeholder for now
#-----------------------------------------------------------
@app.get("/tournament")
@login_required
def show_tournament():
    return render_template("pages/tournament.jinja")


#-----------------------------------------------------------
# Sign in page
# auth.md
#-----------------------------------------------------------
@app.get("/login")
def show_login_form():
    return render_template("pages/login.jinja")


#-----------------------------------------------------------
# Process sign in
# auth.md
#-----------------------------------------------------------
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, username, forename, surname, pass_hash
            FROM users
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash("Unknown user", "error")
            return redirect("/login")

        if not check_password_hash(user["pass_hash"], password):
            flash("Incorrect password", "error")
            return redirect("/login")

        session["logged_in"] = True
        session["user"] = {
            "id":       user["id"],
            "username": user["username"],
            "forename": user["forename"],
            "surname":  user["surname"],
        }

        flash("Login successful", "success")
        return redirect("/")


#-----------------------------------------------------------
# Logout
# auth.md
#-----------------------------------------------------------
@app.get("/logout")
def logout_user():
    session.clear()
    flash("You have been logged out", "success")
    return redirect("/")



#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)