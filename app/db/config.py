#============================================================================
# Teams Tournament + Normal Meetings Database Tables
#============================================================================
# app/db/config.py

class UserTable:

# User table used for login. Only one user is seeded in, but more can be added later. 

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            forename  TEXT NOT NULL,
            surname   TEXT NOT NULL,
            username  TEXT NOT NULL UNIQUE,
            pass_hash TEXT NOT NULL
        )
    """

    # schema.md (test login) states that the given hash password = "test"
    # username = "testington42" password = "test"

    SEED_DATA = """
        INSERT INTO users (forename, surname, username, pass_hash)
        VALUES
            ("Testington", "Testington", "testington42", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252")
    """
    ## schema.md stated that  the given hash password = "test"


class PlayerTable:

    NAME = "players"

    # Every Nelson Chess Club member 
    # used by both TTs (Teams Tournaments) and NM's (Normal Meetings)
    SCHEMA = """
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """

    # Test players are for privacy. 
    # Actual players will be added later. 
    # The names are just for testing purposes and privacy.
    SEED_DATA = """
        INSERT INTO players (name)
        VALUES
            ("Alice"),
            ("Bob"),
            ("Charlie"),
            ("Dana"),
            ("Ethan"),
            ("Fiona"),
            ("George"),
            ("Holly")
    """


class TournamentTable:

    NAME = "tournaments"

    # One row per club night:
    #   type 'TT' = Teams Tournament (has semester, phase and scores)
    #   type 'NM' = Normal Meeting   (just a date)
    SCHEMA = """
        CREATE TABLE tournaments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            type         TEXT NOT NULL DEFAULT 'TT',
            semester_id  INTEGER,
            phase_id     INTEGER,
            date         TEXT,
            team_a_score INTEGER,
            team_b_score INTEGER,
            winning_team TEXT
        )
    """

    SEED_DATA = """
        INSERT INTO tournaments (type, semester_id, phase_id, date)
        VALUES
            ("TT", 1, 7, "2025-01-15")
    """


class MemberTable:

    NAME = "members"

    # Who came to which night. team is only used for TTs (stays empty
    # for normal meetings). payment: "Paid", "Not Paid"
    # links player table to a tournament.
    SCHEMA = """
        CREATE TABLE members (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id  INTEGER NOT NULL,
            member_id      INTEGER NOT NULL,
            team           TEXT,
            payment        TEXT NOT NULL DEFAULT 'Not Paid',

            FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY(member_id)     REFERENCES players(id)
        )
    """

    SEED_DATA = """
        INSERT INTO members (tournament_id, member_id, team)
        VALUES
            (1, 1, "A"),
            (1, 2, "B")
    """


class PointTable:

    NAME = "points"

    # Points are strictly for TTs (Teams Tournaments). 
    # Each player gets +1 point for attending, 
    # and their score for the semester is stored here. 
    # (Yes. That is its ENTIRE purpose. It is a simple table.)
    # winners et +1 point (save_result()) 
    # standings can be calculated from this table.
    SCHEMA = """
        CREATE TABLE points (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id   INTEGER NOT NULL,
            semester_id INTEGER NOT NULL,
            points      INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY(player_id) REFERENCES players(id)
        )
    """

    SEED_DATA = None


#============================================================================
# Table registry - created in this order (linked tables after the ones
# they point to)
#============================================================================

TABLES = [
    UserTable,
    PlayerTable,
    TournamentTable,
    MemberTable,
    PointTable,
]