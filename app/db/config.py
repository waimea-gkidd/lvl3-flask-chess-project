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
    # username = "flumph42" password = "test"

    SEED_DATA = """
        INSERT INTO users (forename, surname, username, pass_hash)
        VALUES
            ("Testington", "Testington", "testington42", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252")
    """
    ## schema.md stated that  the given hash password = "test"


class PlayerTable:

    NAME = "players"

    # Every Nelson Chess Club member - 
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
    #   type 'CL' = one week of a certain class (date + class id)
    SCHEMA = """
        CREATE TABLE tournaments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            type         TEXT NOT NULL DEFAULT 'TT',
            semester_id  INTEGER,
            phase_id     INTEGER,
            date         TEXT,
            team_a_score INTEGER,
            team_b_score INTEGER,
            winning_team TEXT,
            class_id     INTEGER,

            FOREIGN KEY(class_id) REFERENCES classes(id),
        )
    """

    SEED_DATA = """
        INSERT INTO tournaments (type, semester_id, phase_id, date)
        VALUES
            ("TT", 1, 7, "Wed 6 August")
    """


class MemberTable:

    NAME = "members"

    # Who came to which night. team is only used for TTs (stays empty
    # for normal meetings). payment: "Paid", "Not Paid" or "Invoiced" to come soon 
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

    # One row per player per semester - their running total
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
# Classes database tables
#============================================================================

class CourseTable:

    NAME = "courses"
    # Different courses, e.g. Checkmate Pawn, Checkmate Knight
    SCHEMA = """
        CREATE TABLE courses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
        )
    """

    SEED_DATA = """
        INSERT INTO courses (name)
        VALUES
            ("Checkmate Pawn"),
            ("Checkmate Knight")
    """
class ClassTable:

    NAME = "classes"
    # one row per class, each class has its own card on home
    # colour = which of the given colours the class gets on a card and its main page
    # position = which order the class appears on the home page (1 = top, 2 = second, etc)
    SCHEMA = """
        CREATE TABLE classes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id   INTEGER NOT NULL,
            code        TEXT NOT NULL,
            venue      TEXT NOT NULL,
            day         TEXT NOT NULL,
            time        TEXT NOT NULL,
            colour      TEXT NOT NULL,
            position    INTEGER NOT NULL,

            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """
    # Rami's current classes in his order of the week (Monday to Friday).
    # course id 1 = Checkmate Pawn, course id 2 = Checkmate Knight
    SEED_DATA = """
        INSERT INTO classes (course_id, code, venue, day, time, colour, position)
        VALUES
            (2, "CMN", "Card Merchant Nelson", "Monday", "4:00-5:00pm", "knight", 1),
            (1, "VCC", "Victory Community Centre", "Tuesday", "3:30-4:30pm", "pawn", 2),
            (1, "RTH", "Richmond Town Hall", "Wednesday", "3:30-4:30pm", "pawn", 3),
            (2, "NIS", "Nelson Intermediate School", "Thursday", "3:00-4:00pm", "knight", 4),
            (1, "MS", "Māpua School", "Friday", "3:00-4:00pm", "pawn", 5),
            (1, "MHS", "Motueka High School", "Friday", "4:30-5:30pm", "pawn", 6)    """

class StudentTable:

    NAME = "students"

    # Kids who are enrolled in a class. 
    # Each student is linked to a class. Added to multiple classes if they are enrolled in more than one.
    # photo is for photo consent (as some parents may find it sensitive). 
    SCHEMA = """
        CREATE TABLE students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id    INTEGER NOT NULL,
            name        TEXT NOT NULL,
            parent TEXT,
            email TEXT,
            phone TEXT,
            photo TEXT NOT NULL DEFAULT 'TBD',
            

            FOREIGN KEY(class_id) REFERENCES classes(id),
        )
    """
    # ofcourse these are fake students for testing purposes. Actual students will be added later.
    SEED_DATA = """
        INSERT INTO students (class_id, name, parent, email, phone, photo)
        VALUES
            (1, "Alice Smith", "John Smith", "alice@example.com", "123-456-7890", "Y"),
            (1, "Bob Johnson", "Jane Johnson", "bob@example.com", "098-765-4321", "N"),
            (2, "Charlie Brown", "Diana Brown", "charlie@example.com", "555-1234", "TBD"),
            (2, "Diana Wilson", "Robert Wilson", "diana@example.com", "555-5678", "Y"),
            (3, "Eve Davis", "Michael Davis", "eve@example.com", "555-9012", "N"),
            (3, "Frank Miller", "Lisa Miller", "frank@example.com", "555-3456", "Y"),
            (4, "Grace Lee", "David Lee", "grace@example.com", "555-7890", "N"),
            (4, "Henry Taylor", "Sarah Taylor", "henry@example.com", "555-2345", "TBD")
    """

class AttendanceTable:

    NAME = "attendance"

    # Attendees of classes weekly 
    # same as members table but for classes instead of players.
    SCHEMA = """
        CREATE TABLE attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            student_id  INTEGER NOT NULL,

            FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY(student_id) REFERENCES students(id)
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
    CourseTable,
    ClassTable,
    StudentTable,
    TournamentTable,
    MemberTable,
    PointTable,
    AttendanceTable
]