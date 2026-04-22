#!usr/bin/env python3
import os

from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import login_user, LoginManager, current_user, login_required
from services import load_repertoire, fetch_composer

from models import db, User, createUser
from forms import UserForm, LoginForm

# App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize db
db.init_app(app)

# create tables
with app.app_context():
    db.create_all()

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = UserForm()

    if form.validate_on_submit():
        uname = form.uname.data
        pw = form.pw.data

        created = createUser(uname, pw)

        if created:
            flash("Registered Successfully!")
        else:
            flash("User already exists with username " + uname)

        return redirect(url_for('index'))

    return render_template("register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(uname=form.uname.data).first()

        if user is not None and user.verify_password(form.pw.data):
            login_user(user)

            next_page = request.args.get("next")
            if next_page is None or not next_page.startswith("/"):
                next_page = url_for("index")

            flash("Login Success!")
            return redirect(next_page)

        flash("Invalid username or password")

    return render_template("login.html", form=form)


@app.route("/playedlist")
@login_required
def played():
    return render_template("repstudied.html", current_user=current_user)


@app.route("/")
def index():
    data = load_repertoire()
    return render_template("index.html", data=data)


@app.route("/repertoire")
def repertoire():
    data = load_repertoire()
    return render_template("repertoire.html", repertoire=data)


@app.route("/composer/<name>")
def composer(name):
    composer = fetch_composer(name)
    return render_template("composer.html", composer=composer)


# Run app
if __name__ == '__main__':
    app.run(debug=True)