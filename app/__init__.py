#===========================================================
# CHESS PROJECT
# By Gideon Kidd
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect
from werkzeug.security import check_password_hash
# from werkzeug.security import generate_password_hash
# ^ needed later to make the hash for Rami's real password (auth.md)
from dotenv import load_dotenv
import html
from app.helpers import *

app = Flask(__name__)
#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page: Teams Tournament info (public)
#-----------------------------------------------------------
@app.get("/")
def show_home():
    with connect_db() as db:
        # sqlite.md latest TT session
        sql = "SELECT semester_id, phase_id FROM tournaments WHERE type='TT' ORDER BY id DESC"
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


#===========================================================
# Teams Tournament
#===========================================================

#-----------------------------------------------------------
# Teams Tournament home: every session (public),
# start sessions (Rami only - see template)
#-----------------------------------------------------------
@app.get("/tournament")
def show_tournament_home():
    with connect_db() as db:
        # crud.md newest first, used for TT nights only
        sql = """
            SELECT id, semester_id, phase_id, date, team_a_score, team_b_score, winning_team
            FROM tournaments
            WHERE type='TT'
            ORDER BY id DESC
        """
        params = ()
        tournaments = db.execute(sql, params).fetchall()

    # latest session's semester/phase pre-fill the start form
    if tournaments:
        next_semester = tournaments[0]["semester_id"]
        next_phase = tournaments[0]["phase_id"]
    else:
        next_semester = 1
        next_phase = 1

    return render_template(
        "pages/tournament_home.jinja",
        tournaments=tournaments,
        next_semester=next_semester,
        next_phase=next_phase,
    )


#-----------------------------------------------------------
# Current standings: this semester's points (public)
#-----------------------------------------------------------
@app.get("/tournament/standings")
def show_standings():
    with connect_db() as db:
        # sqlite.md the current semester is the latest TT session's semester
        sql = "SELECT semester_id FROM tournaments WHERE type='TT' ORDER BY id DESC"
        params = ()
        latest = db.execute(sql, params).fetchone()

        if latest:
            semester = latest["semester_id"]
        else:
            semester = None

        # JOIN gets each players name with their points, highest first
        # messages project AS renames 'points' to 'total'
        sql = """
            SELECT players.name, points.points AS total
            FROM points
            JOIN players ON points.player_id = players.id
            WHERE points.semester_id=?
            ORDER BY points.points DESC
        """
        params = (semester,)
        standings = db.execute(sql, params).fetchall()

    return render_template("pages/standings.jinja", semester=semester, standings=standings)


#-----------------------------------------------------------
# View one session: result and who was there (public)
#-----------------------------------------------------------
@app.get("/tournament/<int:id>")
def show_session(id):
    with connect_db() as db:
        # sqlite.md
        sql = """
            SELECT semester_id, phase_id, date, team_a_score, team_b_score, winning_team
            FROM tournaments
            WHERE id=?
        """
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

        # JOIN gets names of players on team A
        sql = """
            SELECT members.id, members.payment, players.name
            FROM members
            JOIN players ON members.member_id = players.id
            WHERE members.tournament_id=? AND members.team='A'
        """
        params = (id,)
        team_a = db.execute(sql, params).fetchall()

        # same again for team B
        sql = """
            SELECT members.id, members.payment, players.name
            FROM members
            JOIN players ON members.member_id = players.id
            WHERE members.tournament_id=? AND members.team='B'
        """
        params = (id,)
        team_b = db.execute(sql, params).fetchall()

    return render_template(
        "pages/session.jinja",
        tournament_id=id,
        tt_semester=tournament["semester_id"],
        tt_phase=tournament["phase_id"],
        tournament=tournament,
        team_a=team_a,
        team_b=team_b,
    )


#-----------------------------------------------------------
# Start a new TT session
#-----------------------------------------------------------
@app.post("/tournament/new")
@login_required
def start_tournament():
    # forms.md
    date = request.form.get('date', '').strip()
    semester = request.form.get('semester', '').strip()
    phase = request.form.get('phase', '').strip()

    if not date:
        flash("Session date is required", "error")
        return redirect("/tournament")

    if not semester.isdigit() or not phase.isdigit():
        flash("Semester and phase should be whole numbers", "error")
        return redirect("/tournament")

    date = html.escape(date)

    with connect_db() as db:
        # sqlite.md add the session and get its new id back
        sql = "INSERT INTO tournaments (semester_id, phase_id, date) VALUES (?, ?, ?)"
        params = (int(semester), int(phase), date)
        result = db.execute(sql, params)
        new_id = result.lastrowid

    flash("New session started", "success")
    return redirect(f"/tournament/{new_id}/attendance")


#-----------------------------------------------------------
# TT Attendance: player list, search, attendance toggles
#-----------------------------------------------------------
@app.get("/tournament/<int:id>/attendance")
@login_required
def show_attendance(id):
    # routes.md
    search = request.args.get('q', '').strip()

    with connect_db() as db:
        # sqlite.md this session's semester/phase for the header
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

    # creatures project player ids from rows
    attending_ids = [row["member_id"] for row in attending_rows]

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
# Toggle player attendance
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/attendance/<int:player_id>")
@login_required
def toggle_attendance(id, player_id):
    # routes.md - player id comes from the url, no hidden input needed
    with connect_db() as db:
        sql = "SELECT id FROM members WHERE tournament_id=? AND member_id=?"
        params = (id, player_id)
        existing = db.execute(sql, params).fetchone()

        if existing:
            # attending? = revoke their attendance privileges!
            sql = "DELETE FROM members WHERE id=?"
            params = (existing["id"],)
        else:
            # no attending? = add them to the session (default team = A bc default is needed)
            sql = "INSERT INTO members (tournament_id, member_id, team) VALUES (?, ?, 'A')"
            params = (id, player_id)
        db.execute(sql, params)

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
# TT Teams: attending players with team toggles
#-----------------------------------------------------------
@app.get("/tournament/<int:id>/teams")
@login_required
def show_teams(id):
    with connect_db() as db:
        # sqlite.md this session's semester/phase for header
        sql = "SELECT semester_id, phase_id FROM tournaments WHERE id=?"
        params = (id,)
        tournament = db.execute(sql, params).fetchone()

        # JOIN gets everyone attending with their names
        # id is the members row, team toggle uses it
        sql = """
            SELECT members.id, members.team, members.payment, players.name
            FROM members
            JOIN players ON members.member_id = players.id
            WHERE members.tournament_id=?
        """
        params = (id,)
        members = db.execute(sql, params).fetchall()

    return render_template(
        "pages/teams.jinja",
        tournament_id=id,
        tt_semester=tournament["semester_id"],
        tt_phase=tournament["phase_id"],
        members=members,
    )


#-----------------------------------------------------------
# TT Teams: flip one player between Team A and Team B
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/team/<int:row_id>")
@login_required
def toggle_team(id, row_id):
    # routes.md - row_id comes from the url. its the members row, not the player id
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
# TT Teams: flip player between Paid and Not Paid
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/payment/<int:row_id>")
@login_required
def toggle_payment(id, row_id):
    # routes.md same as toggle_team
    with connect_db() as db:
        sql = "SELECT payment FROM members WHERE id=?"
        params = (row_id,)
        member = db.execute(sql, params).fetchone()

        # Paid flips to Not Paid, else flips to Paid
        if member["payment"] == "Paid":
            payment = "Not Paid"
        else:
            payment = "Paid"

        sql = "UPDATE members SET payment=? WHERE id=?"
        params = (payment, row_id)
        db.execute(sql, params)

        return redirect(f"/tournament/{id}")
#-----------------------------------------------------------
# TT Result: score entry form, or the saved result
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
# TT Result: save scores, +1 point to each winner, then
# back to the Teams Tournament home
#-----------------------------------------------------------
@app.post("/tournament/<int:id>/result")
@login_required
def save_result(id):
    # forms.md admin enters scores for each team, then the winning team gets +1 point for each player on said winning team
    team_a_score = request.form.get('team_a_score', '').strip()
    team_b_score = request.form.get('team_b_score', '').strip()

    if not team_a_score.isdigit() or not team_b_score.isdigit():
        flash("Scores should be whole numbers", "error")
        return redirect(f"/tournament/{id}/result")

    team_a_score = int(team_a_score)
    team_b_score = int(team_b_score)

    # Higher score wins same score = a draw
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

        # Only save once, so ghat points never need undoing 
        # (unless rather incomprehensibly the admin wants to delete the whole session and start session again)
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
            # Does player have points row this semester?
            sql = "SELECT id, points FROM points WHERE player_id=? AND semester_id=?"
            params = (winner["member_id"], tournament["semester_id"])
            existing = db.execute(sql, params).fetchone()

            if existing:
                # Yes add 1
                sql = "UPDATE points SET points=? WHERE id=?"
                params = (existing["points"] + 1, existing["id"])
            else:
                # No default to 1
                sql = "INSERT INTO points (player_id, semester_id, points) VALUES (?, ?, 1)"
                params = (winner["member_id"], tournament["semester_id"])
            db.execute(sql, params)

    flash("Result saved", "success")
    return redirect("/tournament")


#===========================================================
# Normal Meetings (Rami only): same table as TTs, type 'NM'
#===========================================================

#-----------------------------------------------------------
# Normal Meetings home: every (past) meeting, start a new one
#-----------------------------------------------------------
@app.get("/meeting")
@login_required
def show_meeting_home():
    with connect_db() as db:
        # crud.md newest first, NM nights only
        sql = "SELECT id, date FROM tournaments WHERE type='NM' ORDER BY id DESC"
        params = ()
        meetings = db.execute(sql, params).fetchall()

    return render_template("pages/normal_meeting.jinja", meetings=meetings)


#-----------------------------------------------------------
# View one meeting: attendees
#-----------------------------------------------------------
@app.get("/meeting/<int:id>")
@login_required
def show_meeting(id):
    with connect_db() as db:
        # sqlite.md
        sql = "SELECT date FROM tournaments WHERE id=?"
        params = (id,)
        meeting = db.execute(sql, params).fetchone()

        # Ancestry Tracker - JOIN gets the names of everyone who came
        sql = """
            SELECT members.id, members.payment, players.name
            FROM members
            JOIN players ON members.member_id = players.id
            WHERE members.tournament_id=?
        """
        params = (id,)
        attended = db.execute(sql, params).fetchall()

    return render_template(
        "pages/meeting.jinja",
        meeting_id=id,
        meeting_date=meeting["date"],
        attended=attended,
    )


#-----------------------------------------------------------
# Start a new meeting
#-----------------------------------------------------------
@app.post("/meeting/new")
@login_required
def start_meeting():
    # forms.md
    date = request.form.get('date', '').strip()

    if not date:
        flash("Meeting date is required", "error")
        return redirect("/meeting")

    date = html.escape(date)

    with connect_db() as db:
        # sqlite.md add meeting get new id
        sql = "INSERT INTO tournaments (type, date) VALUES ('NM', ?)"
        params = (date,)
        result = db.execute(sql, params)
        new_id = result.lastrowid

    flash("New meeting started", "success")
    return redirect(f"/meeting/{new_id}/attendance")


#-----------------------------------------------------------
# NM Attendance: player list, search, attendance toggles
#-----------------------------------------------------------
@app.get("/meeting/<int:id>/attendance")
@login_required
def show_meeting_attendance(id):
    # routes.md
    search = request.args.get('q', '').strip()

    with connect_db() as db:
        # sqlite.md meeting's date for the header
        sql = "SELECT date FROM tournaments WHERE id=?"
        params = (id,)
        meeting = db.execute(sql, params).fetchone()

        if search:
            # routes.md
            sql = "SELECT id, name FROM players WHERE name LIKE ?"
            params = (f"%{search}%",)
        else:
            sql = "SELECT id, name FROM players"
            params = ()
        players = db.execute(sql, params).fetchall()

        # Who's already attending this meeting
        sql = "SELECT member_id FROM members WHERE tournament_id=?"
        params = (id,)
        attending_rows = db.execute(sql, params).fetchall()

    # creatures project player ids from rows
    attending_ids = [row["member_id"] for row in attending_rows]

    return render_template(
        "pages/meeting_attendance.jinja",
        meeting_id=id,
        meeting_date=meeting["date"],
        players=players,
        attending_ids=attending_ids,
        search=search,
    )


#-----------------------------------------------------------
# Toggle one player's meeting attendance on/off
#-----------------------------------------------------------
@app.post("/meeting/<int:id>/attendance/<int:player_id>")
@login_required
def toggle_meeting_attendance(id, player_id):
    # routes.md player id from url
    with connect_db() as db:
        sql = "SELECT id FROM members WHERE tournament_id=? AND member_id=?"
        params = (id, player_id)
        existing = db.execute(sql, params).fetchone()

        if existing:
            # Attending: remove!
            sql = "DELETE FROM members WHERE id=?"
            params = (existing["id"],)
        else:
            # No atend?: add they ahh!
            sql = "INSERT INTO members (tournament_id, member_id) VALUES (?, ?)"
            params = (id, player_id)
        db.execute(sql, params)

    return redirect(f"/meeting/{id}/attendance")
#-----------------------------------------------------------
# Flip one player's meeting payment between Paid and Not Paid
#-----------------------------------------------------------
@app.post("/meeting/<int:id>/payment/<int:row_id>")
@login_required
def toggle_meeting_payment(id, row_id):
    # same as toggle_payment, route to meeting page instead
    with connect_db() as db:
        sql = "SELECT payment FROM members WHERE id=?"
        params = (row_id,)
        member = db.execute(sql, params).fetchone()

        if member["payment"] == "Paid":
            payment = "Not Paid"
        else:
            payment = "Paid"

        sql = "UPDATE members SET payment=? WHERE id=?"
        params = (payment, row_id)
        db.execute(sql, params)

    return redirect(f"/meeting/{id}")


#-----------------------------------------------------------
# Add a new player to the club (from a meeting)
#-----------------------------------------------------------
@app.post("/meeting/<int:id>/player")
@login_required
def add_meeting_player(id):
    # forms.md
    name = request.form.get('name', '').strip()

    if not name:
        flash("Player name is required", "error")
        return redirect(f"/meeting/{id}/attendance")

    name = html.escape(name)

    # sqlite.md
    with connect_db() as db:
        sql = "INSERT INTO players (name) VALUES (?)"
        params = (name,)
        db.execute(sql, params)

    flash(f"Player '{name}' added", "success")
    return redirect(f"/meeting/{id}/attendance")


#===========================================================
# Sign in / out
#===========================================================

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