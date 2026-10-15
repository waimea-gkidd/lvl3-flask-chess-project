#===========================================================
# CHESS PROJECT
# By Gideon Kidd
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Teams Tournament info (public)
#-----------------------------------------------------------
@app.get("/")
def show_home():
    with connect_db() as db:
        # sqlite.md - latest session
        sql = "SELECT semester_id, phase_id FROM tournaments ORDER BY id DESC LIMIT 1"
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
        tt_day="Wed",
        tt_location="Tahunanui Community Hub",
        tt_semester=tt_semester,
        tt_phase=tt_phase,
    )


#-----------------------------------------------------------
# Teams Tournament home - every session (public),
# start sessions (Rami only - see template)
#-----------------------------------------------------------
@app.get("/tournament")
def show_tournament_home():
    with connect_db() as db:
        # crud.md - newest first
        sql = """
            SELECT id, semester_id, phase_id, date, team_a_score, team_b_score, winning_team
            FROM tournaments
            ORDER BY id DESC
        """
        params = ()
        tournaments = db.execute(sql, params).fetchall()

    return render_template("pages/tournament_home.jinja", tournaments=tournaments)


#-----------------------------------------------------------
# Current standings - this semester's points (public)
#-----------------------------------------------------------
@app.get("/tournament/standings")
def show_standings():
    with connect_db() as db:
        # sqlite.md - the current semester is the latest session's semester
        sql = "SELECT semester_id FROM tournaments ORDER BY id DESC LIMIT 1"
        params = ()
        latest = db.execute(sql, params).fetchone()

        if latest:
            semester = latest["semester_id"]
        else:
            semester = None

        # Add up each player's phase points for this semester, highest first
        sql = """
            SELECT player_id, SUM(points) AS total
            FROM points
            WHERE semester_id=?
            GROUP BY player_id
            ORDER BY total DESC
        """
        params = (semester,)
        totals = db.execute(sql, params).fetchall()

        # Look up each player's name one at a time (no JOINs)
        standings = []
        for row in totals:
            sql = "SELECT name FROM players WHERE id=?"
            params = (row["player_id"],)
            player = db.execute(sql, params).fetchone()

            standings.append({"name": player["name"], "total": row["total"]})

    return render_template("pages/standings.jinja", semester=semester, standings=standings)


#-----------------------------------------------------------
# Start a new TT session
#-----------------------------------------------------------
@app.post("/tournament/new")
@login_required
def start_tournament():
    with connect_db() as db:
        # sqlite.md - carry the last session's semester/phase forward
        sql = "SELECT semester_id, phase_id FROM tournaments ORDER BY id DESC LIMIT 1"
        params = ()
        last = db.execute(sql, params).fetchone()

        if last:
            semester_id = last["semester_id"]
            phase_id = last["phase_id"]
        else:
            semester_id = 1
            phase_id = 1

        # sqlite.md - add the session and get its new id back
        sql = "INSERT INTO tournaments (semester_id, phase_id) VALUES (?, ?)"
        params = (semester_id, phase_id)
        result = db.execute(sql, params)
        new_id = result.lastrowid

    flash("New session started", "success")
    return redirect(f"/tournament/{new_id}/attendance")


#-----------------------------------------------------------
# TT Attendance - player list, search, attendance toggles
#-----------------------------------------------------------
@app.get("/tournament/<int:id>/attendance")
@login_required
def show_attendance(id):
    # routes.md
    search = request.args.get('q', '').strip()

    with connect_db() as db:
        # sqlite.md - this session's semester/phase for the header
        sql = "SELECT semester_id, phase_id FROM tournaments WHERE id=?"
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

        if search:
            # routes.md
            sql = "SELECT id, name FROM players WHERE name LIKE ?"
            params = (f"%{search}%",)
        else:
            sql = "SELECT id, name FROM players"
            params = ()
        players = db.execute(sql, params).fetchall()

        # Who's already attending this session
        sql = "SELECT member_id FROM members WHERE tournament_id=?"
        params = (id,)
        attending_rows = db.execute(sql, params).fetchall()

    attending_ids = []
    for row in attending_rows:
        attending_ids.append(row["member_id"])

    return render_template(
        "pages/attendance.jinja",
        tournament_id=id,
        tt_semester=tournament["semester_id"],
        tt_phase=tournament["phase_id"],
        players=players,
        attending_ids=attending_ids,
        search=search,
    )


#-----------------------------------------------------------
# Toggle one player's attendance on/off
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/attendance/toggle")
@login_required
def toggle_attendance(id):
    # forms.md
    player_id = request.form.get('player_id', '').strip()
    search = request.form.get('search', '').strip()

    with connect_db() as db:
        sql = "SELECT id FROM members WHERE tournament_id=? AND member_id=?"
        params = (id, player_id)
        existing = db.execute(sql, params).fetchone()

        if existing:
            # Already attending - remove them
            sql = "DELETE FROM members WHERE id=?"
            params = (existing["id"],)
        else:
            # Not attending - add them, starting on Team A
            sql = "INSERT INTO members (tournament_id, member_id, team) VALUES (?, ?, 'A')"
            params = (id, player_id)
        db.execute(sql, params)

    # routes.md - keep the search term if there was one
    if search:
        return redirect(f"/tournament/{id}/attendance?q={search}")
    return redirect(f"/tournament/{id}/attendance")


#-----------------------------------------------------------
# Add a new player to the club
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/player")
@login_required
def add_player(id):
    # forms.md
    name = request.form.get('name', '').strip()

    if not name:
        flash("Player name is required", "error")
        return redirect(f"/tournament/{id}/attendance")

    name = html.escape(name)

    # sqlite.md
    with connect_db() as db:
        sql = "INSERT INTO players (name) VALUES (?)"
        params = (name,)
        db.execute(sql, params)

    flash(f"Player '{name}' added", "success")
    return redirect(f"/tournament/{id}/attendance")


#-----------------------------------------------------------
# Done picking players - on to Setup Teams
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/attendance/done")
@login_required
def finish_attendance(id):
    return redirect(f"/tournament/{id}/teams")


#-----------------------------------------------------------
# TT Teams - attending players with team toggles
#-----------------------------------------------------------
@app.get("/tournament/<int:id>/teams")
@login_required
def show_teams(id):
    with connect_db() as db:
        # sqlite.md - this session's semester/phase for the header
        sql = "SELECT semester_id, phase_id FROM tournaments WHERE id=?"
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

        # Everyone attending this session
        sql = "SELECT id, member_id, team FROM members WHERE tournament_id=?"
        params = (id,)
        member_rows = db.execute(sql, params).fetchall()

        # Look up each player's name one at a time (no JOINs)
        members = []
        for row in member_rows:
            sql = "SELECT name FROM players WHERE id=?"
            params = (row["member_id"],)
            player = db.execute(sql, params).fetchone()

            members.append({"id": row["id"], "name": player["name"], "team": row["team"]})

    return render_template(
        "pages/teams.jinja",
        tournament_id=id,
        tt_semester=tournament["semester_id"],
        tt_phase=tournament["phase_id"],
        members=members,
    )


#-----------------------------------------------------------
# TT Teams - flip one player between Team A and Team B
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/team/toggle")
@login_required
def toggle_team(id):
    # forms.md - row_id is the members row, not the player id
    row_id = request.form.get('row_id', '').strip()

    with connect_db() as db:
        sql = "SELECT team FROM members WHERE id=?"
        params = (row_id,)
        member = db.execute(sql, params).fetchone()

        # A flips to B, anything else flips to A
        if member["team"] == "A":
            team = "B"
        else:
            team = "A"

        sql = "UPDATE members SET team=? WHERE id=?"
        params = (team, row_id)
        db.execute(sql, params)

    return redirect(f"/tournament/{id}/teams")


#-----------------------------------------------------------
# TT Result - score entry form, or the saved result
#-----------------------------------------------------------
@app.get("/tournament/<int:id>/result")
@login_required
def show_result(id):
    with connect_db() as db:
        # sqlite.md
        sql = """
            SELECT semester_id, phase_id, team_a_score, team_b_score, winning_team
            FROM tournaments
            WHERE id=?
        """
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

    return render_template(
        "pages/result.jinja",
        tournament_id=id,
        tt_semester=tournament["semester_id"],
        tt_phase=tournament["phase_id"],
        tournament=tournament,
    )


#-----------------------------------------------------------
# TT Result - save scores, +1 point to each winner, then
# back to the Teams Tournament home
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/result")
@login_required
def save_result(id):
    # forms.md
    team_a_score = request.form.get('team_a_score', '').strip()
    team_b_score = request.form.get('team_b_score', '').strip()

    if not team_a_score.isdigit() or not team_b_score.isdigit():
        flash("Scores should be whole numbers", "error")
        return redirect(f"/tournament/{id}/result")

    team_a_score = int(team_a_score)
    team_b_score = int(team_b_score)

    # Higher score wins - same score is a draw
    if team_a_score > team_b_score:
        winning_team = "A"
    elif team_b_score > team_a_score:
        winning_team = "B"
    else:
        winning_team = "Draw"

    with connect_db() as db:
        sql = "SELECT semester_id, phase_id, winning_team FROM tournaments WHERE id=?"
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

        # Only save once, so points never need undoing
        if tournament["winning_team"]:
            flash("Result already saved", "error")
            return redirect(f"/tournament/{id}/result")

        # sqlite.md
        sql = "UPDATE tournaments SET team_a_score=?, team_b_score=?, winning_team=? WHERE id=?"
        params = (team_a_score, team_b_score, winning_team, id)
        db.execute(sql, params)

        # Everyone on the winning team (finds nobody on a draw)
        sql = "SELECT member_id FROM members WHERE tournament_id=? AND team=?"
        params = (id, winning_team)
        winners = db.execute(sql, params).fetchall()

        for winner in winners:
            # Does this player already have a points row for this phase?
            sql = "SELECT id, points FROM points WHERE player_id=? AND semester_id=? AND phase_id=?"
            params = (winner["member_id"], tournament["semester_id"], tournament["phase_id"])
            existing = db.execute(sql, params).fetchone()

            if existing:
                # Yes - add 1 to it
                sql = "UPDATE points SET points=? WHERE id=?"
                params = (existing["points"] + 1, existing["id"])
            else:
                # No - start them on 1
                sql = "INSERT INTO points (player_id, semester_id, phase_id, points) VALUES (?, ?, ?, 1)"
                params = (winner["member_id"], tournament["semester_id"], tournament["phase_id"])
            db.execute(sql, params)

    flash("Result saved", "success")
    return redirect("/tournament")


#-----------------------------------------------------------
# Sign in page
#-----------------------------------------------------------
@app.get("/login")
def show_login_form():
    # auth.md
    return render_template("pages/login.jinja")


#-----------------------------------------------------------
# Process sign in
#-----------------------------------------------------------
@app.post("/login")
def login_user():
    # auth.md
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = "SELECT id, username, forename, surname, pass_hash FROM users WHERE username=?"
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
#-----------------------------------------------------------
@app.get("/logout")
def logout_user():
    # auth.md
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