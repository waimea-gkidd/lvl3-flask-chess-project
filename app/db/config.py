#============================================================================
# Teams Tournament Database Tables
#============================================================================
# app/db/config.py

class UserTable:

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

    # This is a TEST account so login works out of the box:
    # username: rami   password: test
    # (this is the exact example hash from docs/guides/schema.md)
    SEED_DATA = """
        INSERT INTO users (forename, surname, username, pass_hash)
        VALUES
            ("Flumph", "Testington", "flumph42", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252")
    """
    ## schema.md stated that the given hash password = "test"
class PlayerTable:

    NAME = "players"

    SCHEMA = """
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """

    SEED_DATA = """
        INSERT INTO players (name)
        VALUES
            ("Alice"),
            ("Bob"),
            ("Charlie"),
            ("Dana")
    """


class MemberTable:

    NAME = "members"

    SCHEMA = """
    CREATE TABLE members (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id  INTEGER NOT NULL,
        member_id      INTEGER NOT NULL,
        team           TEXT,

        FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
        FOREIGN KEY(member_id)     REFERENCES players(id)
    )
"""

    SEED_DATA = """
        INSERT INTO members (team_id, member_id)
        VALUES
            (1, 1),
            (2, 2)
    """


class TournamentTable:

    NAME = "tournaments"

    SCHEMA = """
    CREATE TABLE tournaments (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        semester_id  INTEGER NOT NULL,
        phase_id     INTEGER NOT NULL,
        date         TEXT,
        team_a_score INTEGER,
        team_b_score INTEGER,
        winning_team TEXT
    )
"""

    SEED_DATA = """
        INSERT INTO tournaments (semester_id, phase_id, date)
        VALUES
            (1, 7, "Wed 6 August")
    """


TABLES = [
    UserTable,
    PlayerTable,
    TournamentTable,
    MemberTable
]

#============================================================================
# Casual meetings database tables
#============================================================================


#============================================================================
# Classes database tables
#============================================================================