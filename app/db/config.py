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
            ("Rami", "Admin", "rami", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252")
    """

class PlayerTable:

    NAME = "players"

    SCHEMA = """
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """

    SEED_DATA = """
        INSERT INTO players (id, name)
        VALUES
            ("1","Alice"),
            ("2","Bob"),
            ("3","Charlie"),
            ("4","Dana")
    """


class MemberTable:

    NAME = "members"

    SCHEMA = """
        CREATE TABLE members (
            team_id   INTEGER PRIMARY KEY,
            member_id INTEGER NOT NULL,

            FOREIGN KEY(member_id) REFERENCES players(id)
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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            semester_id INTEGER,
            phase_id    INTEGER,
            team1_id    INTEGER,
            team2_id    INTEGER,
            win_id      INTEGER,

            FOREIGN KEY(team1_id) REFERENCES members(team_id),
            FOREIGN KEY(team2_id) REFERENCES members(team_id),
            FOREIGN KEY(win_id)   REFERENCES members(team_id)
        )
    """

    SEED_DATA = """
        INSERT INTO tournaments (semester_id, phase_id, team1_id, team2_id, win_id)
        VALUES
            (1, 1, 1, 2, 1),
            (1, 2, 1, 2, 1),

    """


TABLES = [
    UserTable,
    PlayerTable,
    MemberTable,
    TournamentTable,
]

#============================================================================
# Casual meetings database tables
#============================================================================


#============================================================================
# Classes database tables
#============================================================================