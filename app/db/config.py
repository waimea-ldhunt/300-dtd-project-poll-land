#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class users:

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            pass_hash   TEXT NOT NULL,
            image_path  TEXT DEFAULT "_default-profile.png",
            is_creator  INTEGER DEFAULT 0,
            is_admin    INTEGER DEFAULT 0
        )
    """

    SEED_DATA = """
        INSERT INTO users (id, username, image_path, pass_hash, is_creator, is_admin)
        VALUES
            (0, "John Poll", "default-profile.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 0, 1),
            (1, "Mac's Donald", "f2676cd1bb52_MacsDonaldLogo.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 1, 0),
            (2, "Burgerlover6", "8ae8482e6cf3_Meal.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 0, 0),
            (3, "Sauceking", "6fdafad96a3c_crown.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 0, 0),
            (4, "Notflix", "de87ab1bdcd7_NotflixLogo.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 1, 0),
            (5, "Seat_Potato", "88f1612b8214_Potato.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 0, 0),
            (6, "SirEdwingtonIII", "a9961fb25272_Edwington.png", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", 0, 0)
    """

class polls:

    NAME = "polls"

    SCHEMA = """
        CREATE TABLE polls (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            subtitle    TEXT,
            image_path  TEXT,
            is_public   INTEGER DEFAULT 0,
            
            owner_id    INTEGER NOT NULL,
            
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )
    """

    SEED_DATA = """
        INSERT INTO polls (id, owner_id, title, subtitle, image_path, is_public)
        VALUES
            (0, 1, "Big Matt", "How do we feel about our new 'Big Matt' burger?", "3c9c71124181_burger-png-without-background_JXZO.png", 1),
            (1, 1, "Secret Sauce", "Which Flavour should our new 'Secret Sauce' be?", "136e785a19fc_SAUCE.png", 0),
            (2, 4, "New Season Competition", "Which show should get a new season?", NULL, 1),
            (3, 4, "Subscription", "Should we increase our subscription costs?", 0ee857a361d2_money.png, 0)
    """

class options:

    NAME = "options"

    SCHEMA = """
        CREATE TABLE options (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            text        TEXT NOT NULL,
            
            poll_id     INTEGER NOT NULL,
            
            FOREIGN KEY(poll_id) REFERENCES polls(id)
        )
    """

    SEED_DATA = """
        INSERT INTO options (id, poll_id, text)
        VALUES
            (0, 0, "Love It!"),
            (1, 0, "Hate It."),
            (2, 1, "BBQ"),
            (3, 1, "Pineapple"),
            (4, 1, "Concrete"),
            (5, 2, "Wierder Stuff"),
            (6, 2, "Cephalopod Challenge"),
            (7, 2, "Fixing Good"),
            (8, 3, "Yes"),
            (9, 3, "Super Yes")
    """

class votes:

    NAME = "votes"

    SCHEMA = """
        CREATE TABLE votes (
            poll_id     INTEGER NOT NULL,
            option_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            
            FOREIGN KEY(poll_id) REFERENCES polls(id),
            FOREIGN KEY(option_id) REFERENCES options(id),
            FOREIGN KEY(user_id) REFERENCES users(id),

            PRIMARY KEY(poll_id, option_id, user_id)
        )
    """

    SEED_DATA = """
        INSERT INTO votes (poll_id, option_id, user_id)
        VALUES
            (0, 0, 2),
            (0, 0, 3),
            (0, 1, 5),
            (2, 5, 5),
            (2, 7, 6),
            (3, 9, 6)
    """

class participants:

    NAME = "participants"

    SCHEMA = """
        CREATE TABLE participants (
            poll_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            
            FOREIGN KEY(poll_id) REFERENCES polls(id),
            FOREIGN KEY(user_id) REFERENCES users(id),

            PRIMARY KEY(poll_id, user_id)
        )
    """

    SEED_DATA = """
        INSERT INTO participants (poll_id, user_id)
        VALUES
            (1, 3),
            (1, 6),
            (3, 5),
            (3, 6)
    """

class comments:

    NAME = "comments"

    SCHEMA = """
        CREATE TABLE comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            text        TEXT NOT NULL,
            
            poll_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            
            FOREIGN KEY(poll_id) REFERENCES polls(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """

    SEED_DATA = """
        INSERT INTO comments (id, text, poll_id, user_id)
        VALUES
            (0, "I LOVE THE BIG MATT!", 0, 2)
    """


#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    users,
    polls,
    options,
    votes,
    participants,
    comments,
]

