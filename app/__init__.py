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
import random
import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

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
            SELECT username
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM polls
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

        sql = """
            SELECT *
            FROM participants
        """
        params = ()
        participants = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM comments
        """
        params = ()
        comments = db.execute(sql, params).fetchall()

        vote_groups = [
            (vote["poll_id"], vote["user_id"])
            for vote in votes
        ]

        return render_template(
            "pages/home.jinja",
            users=users,
            polls=polls,
            options=options,
            votes=votes,
            vote_groups=vote_groups,
            comments=comments
        )

@app.get("/participating")
@login_required
def participating_page():
    with connect_db() as db:

        sql = """
            SELECT *
            FROM polls
        """
        params = ()
        polls = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM users
        """
        params = ()
        users = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM options
        """
        params = ()
        options = db.execute(sql, params).fetchall()
        
        sql = """
            SELECT poll_id
            FROM participants
            WHERE user_id=?
        """
        params = (session["user"]["id"],)
        participating_polls = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM votes
        """
        params = ()
        votes = db.execute(sql, params).fetchall()

        vote_groups = [
            (vote["poll_id"], vote["user_id"])
            for vote in votes
        ]

        return render_template(
            "pages/participating.jinja",
            polls=polls,
            users=users,
            options=options,
            participating_polls=participating_polls,
            votes=votes,
            vote_groups=vote_groups
        )
    
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

@login_required
@app.get("/logout")
def logout_user():
    session.clear()
    flash("Logged Out Successfully", "success")
    return redirect("/")

@login_required
@app.get("/create")
def create_page():
    if session['user']['is_creator']:
        return render_template("pages/create_poll.jinja")
    else:
        flash("You do not have permission to access this page.","error")
        return redirect("/")
    
@login_required
@app.post("/poll/create")
def create_poll():
    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()
    is_public = request.form.get('is_creator')
    options = request.form.getlist('option')

    if is_public == 'on': is_public = 1
    else: is_public = 0

    image = request.files.get('image', None)
    
    if image and not image.filename == '':
        unique_filename = save_image(image)
    else:
        unique_filename = None

    with connect_db() as db:

        sql = """
           INSERT INTO polls (title, subtitle, is_public, owner_id, image_path)
           VALUES (?, ?, ?, ?, ?)
        """
        params = (title, subtitle, is_public, session['user']['id'], unique_filename)
        cursor = db.execute(sql, params)
        poll_id = cursor.lastrowid

        for option in options:
            sql = """
               INSERT INTO options (text, poll_id)
               VALUES (?, ?)
            """
            params = (option, poll_id)
            db.execute(sql, params)

        if is_public == 0:
            participants = int(request.form.get('participants'))

            sql = """
                SELECT id, is_creator, is_admin
                FROM users
            """
            params = ()
            users = db.execute(sql, params).fetchall()

            filtered_users = []
            for user in users:
                if user['is_creator'] == 0 and user['is_admin'] == 0:
                    filtered_users.append(user['id'])

            participating_users = random.sample(filtered_users, participants)

            for user_id in participating_users:
                sql = """
                    INSERT INTO participants (user_id, poll_id)
                    VALUES (?,?)
                    
                """
                params = (user_id, poll_id)
                users = db.execute(sql, params).fetchall
        flash("Poll Created", "success")
        return redirect("/")
    
@login_required
@app.get("/poll/<int:id>/edit")
def edit_poll(id):
    with connect_db() as db:

        sql = """
           SELECT *
           FROM polls
           WHERE id=?
        """
        params = (id,)
        poll = db.execute(sql, params).fetchone()

        if session["user"]["is_creator"] and poll["owner_id"] == session["user"]["id"]:

                sql = """
                    SELECT text
                    FROM options
                    WHERE poll_id=?
                """
                params = (id,)
                options = db.execute(sql, params).fetchall()

                if poll["is_public"]:
                    participants = "-"
                else:
                    sql = """
                        SELECT *
                        FROM participants
                        WHERE poll_id=?
                    """
                    params = (id,)
                    participants_out = db.execute(sql, params).fetchall()
                    participants = participants_out.count()

                return render_template("pages/edit_poll.jinja", poll=poll, options=options, participants=participants)
        else:
            flash("You do not have permission to access this page.","error")
            return redirect("/")

@login_required
@app.get("/poll/<int:id>/details")
def poll_details(id):
    with connect_db() as db:

        sql = """
            SELECT *
            FROM polls
            WHERE id=?
        """
        params = (id,)
        poll = db.execute(sql, params).fetchone()

        sql = """
            SELECT *
            FROM options
            WHERE poll_id=?
        """
        params = (id,)
        options = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM votes
            WHERE poll_id=?
        """
        params = (id,)
        votes = db.execute(sql, params).fetchall()

        sql = """
            SELECT *
            FROM participants
            WHERE poll_id=?
        """
        params = (id,)
        participants = db.execute(sql, params).fetchall()

        return render_template("pages/poll.jinja", poll=poll, options=options, votes=votes, participants=participants)


@login_required
@app.post("/poll/<int:id>/update")
def update_poll(id):

    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()

    with connect_db() as db:

        sql = """
            UPDATE polls
            SET title=?, subtitle=?
            WHERE id=?
        """
        params = (title, subtitle, id)
        db.execute(sql, params)

        flash("Changes Saved", "success")
        return redirect("/")

@app.get("/poll/<int:id>/delete")
def delete_poll(id):
    with connect_db() as db:

        sql = """
            DELETE FROM polls
            WHERE id=?
        """
        params = (id,)
        db.execute(sql, params)

        sql = """
            DELETE FROM options
            WHERE poll_id=?
        """
        params = (id,)
        db.execute(sql, params)

        sql = """
            DELETE FROM votes
            WHERE poll_id=?
        """
        params = (id,)
        db.execute(sql, params)

        flash("Poll Deleted", "success") 
        return redirect("/")
    
@login_required
@app.get("/poll/<int:poll_id>/vote/<int:option_id>")
def vote(poll_id, option_id):

    with connect_db() as db:
        
        sql = """
                DELETE FROM votes
                WHERE poll_id=?
                AND user_id=? 
            """
        params = (poll_id, session["user"]["id"])
        db.execute(sql, params)

        sql = """
            INSERT INTO votes (poll_id, option_id, user_id)
            VALUES (?, ?, ?)
        """
        params = (poll_id, option_id, session["user"]["id"])
        db.execute(sql, params)

        flash(f"Vote Added", "success")
        return redirect(request.referrer or "/")


@login_required
@app.get("/poll/<int:poll_id>/unvote")
def revoke_vote(poll_id):
    with connect_db() as db:

        sql = """
            DELETE FROM votes
            WHERE poll_id=?
            AND user_id=? 
        """
        params = (poll_id, session["user"]["id"])
        db.execute(sql, params)

        flash(f"Vote Removed", "success")
        return redirect(request.referrer or "/")

@login_required
@app.post("/poll/<int:id>/comment")
def comment(id):

    text = request.form.get('text', '').strip()

    with connect_db() as db:
        sql = """
            INSERT INTO comments (text, poll_id, user_id)
        """
        params = (text, id, session["user"]["id"])
        db.execute(sql, params)

        flash(f"Comment Added", "success")
        return redirect(request.referrer or "/")

@login_required
@app.get("/comment/<int:id>/delete")
def delete_comment(id):
    with connect_db() as db:
        sql = """
            DELETE FROM comments
            WHERE id=?
        """
        params = (id,)
        db.execute(sql, params)

        flash(f"Comment Deleted", "success")
        return redirect(request.referrer or "/")

@app.get("/profile/<int:id>")
def view_profile(id):
    with connect_db() as db:

        sql = """
            SELECT *
            FROM users
            WHERE id=?
        """
        params = (id,)
        user = db.execute(sql, params).fetchone()

        if session and session["user"]["id"] == id:
            return render_template("pages/profile.jinja", user=user)
        
        elif session and user["is_creator"] == 1:

            sql = """
                SELECT *
                FROM polls
                WHERE owner_id=?
            """
            params = (id,)
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

            sql = """
                SELECT *
                FROM comments
            """
            params = ()
            comments = db.execute(sql, params).fetchall()

            sql = """
                SELECT *
                FROM users
            """
            params = ()
            comments = db.execute(sql, params).fetchall()

            return render_template(
                "pages/other_profile.jinja",
                user=user,
                polls=polls,
                options=options,
                votes=votes,
                comments=comments
            )
            
        else:
            flash(f"This profile is private, you do not have permission to view it", "error")
            return redirect(request.referrer or "/")

@login_required
@app.post("/user/<int:id>/update/username")
def update_profile(id):
    username = request.form.get('username', '').strip()

    with connect_db() as db:

        sql = """
            UPDATE users
            SET username=?
            WHERE id=?
        """
        params = (username, id)
        db.execute(sql, params)

        flash(f"Profile updated", "success")
        return redirect(f"profile/{id}")

@login_required
@app.post("/user/<int:id>/update/image")
def update_profile_image(id):
    image = request.files.get('image', None)

    if not image or image.filename == '':
        flash("There was a problem uploading the image", "error")
        return redirect(request.referrer or "/")

    unique_filename = save_image(image)

    with connect_db() as db:

        sql = """
            UPDATE users
            SET image_path=?
            WHERE id=?
        """
        params = (unique_filename, id)
        db.execute(sql, params)

        flash(f"Profile Picture Updated", "success")
        return redirect(f"profile/{id}")

@login_required
@app.post("/user/<int:id>/update/password")
def update_password(id):
    old_pass = request.form.get('old_password', '').strip()
    new_pass = request.form.get('new_password', '').strip()

    with connect_db() as db:

        sql = """
            SELECT pass_hash
            FROM users
            WHERE id=?
        """
        params = (id,)
        user = db.execute(sql, params).fetchone()
        
        if not check_password_hash(user["pass_hash"], old_pass):
            flash("Old Password Incorrect", "error")
            return redirect(f"/profile/{id}")

        new_hash = generate_password_hash(new_pass)

        sql = """
            UPDATE users
            SET pass_hash=?
            WHERE id=?
        """
        params = (new_hash, id)
        user = db.execute(sql, params).fetchone() 

@login_required
@app.get("/user/<int:id>/delete")
def delete_user(id):
    with connect_db() as db:
        sql = """
            SELECT image_path
            FROM users
            WHERE id=?
        """
        params = (id,)
        user = db.execute(sql, params).fetchone()

        delete_image(user["image_path"])

        sql = """
            DELETE FROM users
            WHERE id=?
        """
        params = (id,)
        db.execute(sql, params)

def save_image(image):
    filename = secure_filename(image.filename)
    random_prefix = uuid.uuid4().hex[:12]
    unique_filename = f"{random_prefix}_{filename}"

    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    image.save(filepath)

    return unique_filename

def delete_image(image_path):
    filepath = os.path.join(UPLOAD_FOLDER, image_path)
    if os.path.exists(filepath):
        os.remove(filepath)

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