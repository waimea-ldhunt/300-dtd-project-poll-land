#===========================================================
# PROJECT NAME HERE
# By YOUR NAME HERE
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
# Home page - Show all notes
#-----------------------------------------------------------
@app.get("/")
def home_page():
    with connect_db() as db:
        sql = """
            SELECT polls.id, polls.owner_id, polls.title, polls.subtitle, users.username
            FROM polls
            INNER JOIN users ON polls.owner_id=users.id;
        """
        params = ()
        polls = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM options
        """
        params = ()
        options = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM votes
        """
        params = ()
        votes = db.execute(sql, params).fetchall()

        return render_template("pages/home.jinja", polls=polls, options=options, votes=votes)
    
@app.get("/login")
def login_page():
    return render_template("pages/login.jinja")

@app.get("/signup")
def signup_page():
    return render_template("pages/signup.jinja")

@app.post("/account/login")
def login_user():

    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        
        sql = """
            SELECT id, username, pass_hash, is_creator, is_admin
            FROM users
            WHERE LOWER(username)=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash("No Account Found", "error")
            return redirect("/login")
        
        if not check_password_hash(user["pass_hash"], password):
            flash("Password Incorrect", "error")
            return redirect("/login")
        
        session["logged_in"] = True
        session["user"] = {
            "id":           user["id"],
            "username":     user["username"],
            "pass_hash":    user["pass_hash"],
            "is_creator":   user["is_creator"],
            "is_admin":     user["is_admin"]
        }

        flash("Logged In Successfully", "success")
        return redirect("/")

@app.post("/account/create")
def create_user():

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    is_creator = request.form.get('is_creator')

    if is_creator == 'on': is_creator = 1
    else: is_creator = 0

    with connect_db() as db:
        
        sql = """
            SELECT *
            FROM users
            WHERE LOWER(username)=?
        """
        params = (username.lower(),)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' Already Exists", "error")
            return redirect("/signup")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (username, pass_hash, is_creator)
            VALUES (?, ?, ?)
        """
        params = (username, pass_hash, is_creator)
        db.execute(sql, params)

        flash(f"Account '{username}' Created, Please Log In", "success")
        return redirect("/login")

@app.get("/logout")
def logout_user():
    session.clear()
    flash("Logged Out Successfully", "success")
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

