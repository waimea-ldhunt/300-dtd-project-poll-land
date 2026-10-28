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
            SELECT *
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
            comments=comments,
            labels=get_labels(polls, options),
            data=get_data(polls, options, votes)
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
            vote_groups=vote_groups,
            labels=get_labels(polls, options),
            data=get_data(polls, options, votes)
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


@app.get("/logout")
@login_required
def logout_user():
    session.clear()
    flash("Logged Out Successfully", "success")
    return redirect("/")

@app.get("/create")
@login_required
def create_page():
    if session['user']['is_creator']:

        with connect_db() as db:

            sql = """
               SELECT id
               FROM users
               WHERE is_creator=0
               AND is_admin=0
            """
            params = ()
            users = db.execute(sql, params).fetchall()
            usercount = len(users)

        return render_template("pages/create_poll.jinja", usercount=usercount)
    else:
        flash("You do not have permission to access this page.","error")
        return redirect("/")
    
@app.post("/poll/create")
@login_required
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
    
@app.get("/poll/<int:id>/edit")
@login_required
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
                    participants = len(participants_out)

                return render_template("pages/edit_poll.jinja", poll=poll, options=options, participants=participants)
        else:
            flash("You do not have permission to access this page.","error")
            return redirect(request.referrer or "/")


@app.get("/poll/<int:id>/details")
@login_required
def poll_details(id):
    with connect_db() as db:

        sql = """
            SELECT *
            FROM polls
            WHERE id=?
        """
        params = (id,)
        poll = db.execute(sql, params).fetchone()

        if not ( session["user"]["is_creator"] == 1 and session["user"]["id"] == poll["owner_id"] ):
            flash("You do not have permission to access this page.","error")
            return redirect(request.referrer or "/")

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

        labels = []
        for option in options:
            if option["poll_id"] == poll["id"]:
                labels.append(str(option["text"]))

        data = []
        for option in options:
            if option["poll_id"] == poll["id"]:
                count = 0
                for vote in votes:
                    if vote["option_id"] == option["id"]:
                        count += 1
                data.append(count)

        print(data)
        print(labels)

        return render_template(
            "pages/poll.jinja",
            poll=poll,
            options=options,
            votes=votes,
            participants=participants,
            labels=labels,
            data=data
        )

@app.post("/poll/<int:id>/update")
@login_required
def update_poll(id):

    title = request.form.get('title', '').strip()
    subtitle = request.form.get('subtitle', '').strip()

    image = request.files.get('image', None)
    
    with connect_db() as db:

            sql = """
                SELECT *
                FROM polls
                WHERE id=?
            """
            params = (id,)
            poll = db.execute(sql, params).fetchone()

            if image:

                unique_filename = save_image(image)

                if poll["image_path"]:
                    delete_image(poll["image_path"])

                sql = """
                    UPDATE polls
                    SET title=?, subtitle=?, image_path=?
                    WHERE id=?
                """
                params = (title, subtitle, unique_filename, id)
                db.execute(sql, params)

                flash("Poll Updated [Image Changed]", "success") 
                return redirect(f"/poll/{id}/details")
        
            else:

                sql = """
                    UPDATE polls
                    SET title=?, subtitle=?
                    WHERE id=?
                """
                params = (title, subtitle, id)
                db.execute(sql, params)

                flash("Poll Updated", "success") 
                return redirect(f"/poll/{id}/details")

@app.get("/poll/<int:id>/delete")
@login_required
def delete_poll(id):
    with connect_db() as db:

        sql = """
            SELECT creator_id
            FROM polls
            WHERE id=?
        """
        params = (id,)
        poll = db.execute(sql, params).fetchone()
        
        if not ( session["user"]["is_creator"] == 1 and session["user"]["id"] == poll["creator_id"] ):
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")

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
    
@app.get("/poll/<int:poll_id>/vote/<int:option_id>")
@login_required
def vote(poll_id, option_id):

    with connect_db() as db:

        if session["user"]["is_admin"] == 0 and session["user"]["is_creator"]:
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")
            
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

@app.get("/poll/<int:poll_id>/unvote")
@login_required
def revoke_vote(poll_id):
    with connect_db() as db:

        if session["user"]["is_admin"] == 0 and session["user"]["is_creator"]:
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")

        sql = """
            DELETE FROM votes
            WHERE poll_id=?
            AND user_id=? 
        """
        params = (poll_id, session["user"]["id"])
        db.execute(sql, params)

        flash(f"Vote Removed", "success")
        return redirect(request.referrer or "/")

@app.post("/poll/<int:id>/comment")
@login_required
def comment(id):

    text = request.form.get('text', '').strip()

    with connect_db() as db:

        sql = """
            SELECT owner_id
            FROM polls
            WHERE id=?
        """
        params = (id,)
        poll = db.execute(sql, params).fetchone()

        if session["user"]["is_admin"] == 1 and  not session["user"]["id"] == poll["owner_id"]:
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")

        sql = """
            INSERT INTO comments (text, poll_id, user_id)
            VALUES (?, ?, ?)
        """
        params = (text, id, session["user"]["id"])
        db.execute(sql, params)

        flash(f"Comment Added", "success")
        return redirect(request.referrer or "/")

@app.get("/comment/<int:id>/delete")
@login_required
def delete_comment(id):
    with connect_db() as db:

        sql = """
            SELECT user_id
            FROM comments
            WHERE id=?
        """
        params = (id,)
        comment = db.execute(sql, params).fetchone()
        
        if session["user"]["is_admin"] == 0 and not session["user"]["id"] == comment["user_id"]:
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")

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

        if session and session["user"]["id"] == id or user["is_creator"] == 1 or session["user"]["is_admin"] == 1:

            sql = """
                SELECT *
                FROM polls
                WHERE owner_id=?
                AND is_public=1
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
            users = db.execute(sql, params).fetchall()

            return render_template(
                "pages/profile.jinja",
                user=user,
                users=users,
                polls=polls,
                options=options,
                votes=votes,
                comments=comments,
                labels=get_labels(polls, options),
                data=get_data(polls, options, votes)
            )
        else:
            flash("You do not have permission to view this profile","error")
            return redirect(request.referrer or "/")

@app.post("/user/<int:id>/update/username")
@login_required
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

        session['user']['username'] = username

        flash(f"Profile updated", "success")
        return redirect(f"/profile/{id}")

@app.post("/user/<int:id>/update/image")
@login_required
def update_profile_image(id):
    image = request.files.get('image', None)

    if not image or image.filename == '':
        flash("There was a problem uploading the image", "error")
        return redirect(f"/profile/{id}")

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
        return redirect(f"/profile/{id}")


@app.post("/user/<int:id>/update/password")
@login_required
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

        session['user']['pass_hash'] = new_hash

        flash("Password Changed","success")
        return redirect(f"/profile/{id}")

@login_required
@app.get("/user/<int:id>/delete")
def delete_user(id):
    with connect_db() as db:

        if session["is_admin"] == 0 and not session["user"]["id"] == id:
            flash("You do not have permission to access this route.","error")
            return redirect(request.referrer or "/")

        sql = """
            SELECT image_path
            FROM users
            WHERE id=?
        """
        params = (id,)
        user = db.execute(sql, params).fetchone()

        if user["image_path"] and not user["image_path"] == "_default-profile.png":
            delete_image(user["image_path"])

        sql = """
            DELETE FROM users
            WHERE id=?
        """
        params = (id,)
        db.execute(sql, params)

        if session["user"]["id"] == id:
            session.clear()

        flash("Account Deleted","success")
        return redirect("/")

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

def get_labels(polls, options):
    labels = []
    for poll in polls:
        poll_labels = []
        for option in options:
            if option["poll_id"] == poll["id"]:
                poll_labels.append(str(option["text"]))
        labels.append(poll_labels)
    return labels

def get_data(polls, options, votes):
    data = []
    for poll in polls:
        poll_data = []
        for option in options:
            if option["poll_id"] == poll["id"]:
                count = 0
                for vote in votes:
                    if vote["option_id"] == option["id"]:
                        count += 1
                poll_data.append(count)
        data.append(poll_data)
    return data
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