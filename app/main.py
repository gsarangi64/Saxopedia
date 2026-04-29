#!usr/bin/env python3
import os

from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from app.services import load_repertoire, fetch_composer

from app.models import (
    db, User, Program, ProgramPiece, StudiedPiece,
    create_user, create_program,
    add_piece_to_program, remove_piece_from_program,
    mark_piece_studied, remove_studied_piece
)
from app.forms import UserForm, LoginForm, ProgramForm, AddPieceForm, StudiedPieceForm

# App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Auth Routes ---

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        created = create_user(form.uname.data, form.pw.data)
        if created:
            flash("Registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Username '{}' is already taken.".format(form.uname.data), "error")
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
            flash("Welcome back, {}!".format(user.uname), "success")
            return redirect(next_page)
        flash("Invalid username or password.", "error")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for('index'))


# --- Core Routes ---

@app.route("/")
def index():
    data = load_repertoire()
    return render_template("index.html", data=data)


@app.route("/repertoire")
@login_required
def repertoire():
    data = load_repertoire()
    programs = current_user.programs.all()
    studied_titles = {
        sp.piece_title for sp in current_user.studied_pieces.all()
    }
    return render_template(
        "repertoire.html",
        repertoire=data,
        programs=programs,
        studied_titles=studied_titles
    )


@app.route("/composer/<name>")
def composer(name):
    composer_data = fetch_composer(name)
    return render_template("composer.html", composer=composer_data)


# --- Program Routes ---

@app.route("/programs")
@login_required
def programs():
    user_programs = current_user.programs.all()
    return render_template("programs.html", programs=user_programs)


@app.route("/programs/create", methods=['POST'])
@login_required
def create_program_route():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Program name cannot be empty.", "error")
        return redirect(request.referrer or url_for('programs'))

    program, error = create_program(name, current_user.id)
    if error:
        flash(error, "error")
    else:
        flash("Program '{}' created!".format(name), "success")
    return redirect(request.referrer or url_for('programs'))


@app.route("/programs/<int:program_id>/delete", methods=['POST'])
@login_required
def delete_program(program_id):
    program = Program.query.filter_by(id=program_id, user_id=current_user.id).first_or_404()
    db.session.delete(program)
    db.session.commit()
    flash("Program '{}' deleted.".format(program.name), "success")
    return redirect(url_for('programs'))


@app.route("/programs/<int:program_id>/remove_piece/<int:piece_id>", methods=['POST'])
@login_required
def remove_from_program(program_id, piece_id):
    # Verify ownership
    program = Program.query.filter_by(id=program_id, user_id=current_user.id).first_or_404()
    remove_piece_from_program(program_id, piece_id)
    flash("Piece removed from program.", "success")
    return redirect(url_for('programs'))


# --- Add Piece to Program (AJAX-friendly POST) ---

@app.route("/addpiece", methods=['POST'])
@login_required
def addpiece():
    piece_title = request.form.get("piece_title", "").strip()
    composer_name = request.form.get("composer", "").strip()
    year = request.form.get("year", "").strip()
    instrumentation = request.form.get("instrumentation", "").strip()
    program_id = request.form.get("program_id", "").strip()

    if not piece_title or not program_id:
        flash("Missing piece or program info.", "error")
        return redirect(url_for('repertoire'))

    # Verify program belongs to current user
    program = Program.query.filter_by(id=int(program_id), user_id=current_user.id).first()
    if not program:
        flash("Program not found.", "error")
        return redirect(url_for('repertoire'))

    success, error = add_piece_to_program(int(program_id), piece_title, composer_name, year, instrumentation)
    if success:
        flash("'{}' added to {}.".format(piece_title, program.name), "success")
    else:
        flash(error, "error")

    return redirect(url_for('repertoire'))


# --- Studied Pieces Routes ---

@app.route("/studied")
@login_required
def studied():
    pieces = current_user.studied_pieces.order_by(StudiedPiece.studied_at.desc()).all()
    programs = current_user.programs.all()
    return render_template("repstudied.html", studied_pieces=pieces, programs=programs)


@app.route("/studied/add", methods=['POST'])
@login_required
def add_studied():
    piece_title = request.form.get("piece_title", "").strip()
    composer_name = request.form.get("composer", "").strip()
    year = request.form.get("year", "").strip()
    instrumentation = request.form.get("instrumentation", "").strip()
    notes = request.form.get("notes", "").strip()

    if not piece_title:
        flash("No piece specified.", "error")
        return redirect(url_for('repertoire'))

    success, error = mark_piece_studied(
        current_user.id, piece_title, composer_name, year, instrumentation, notes
    )
    if success:
        flash("'{}' added to your studied list!".format(piece_title), "success")
    else:
        flash(error, "error")

    return redirect(url_for('repertoire'))


@app.route("/studied/remove/<int:piece_id>", methods=['POST'])
@login_required
def remove_studied(piece_id):
    removed = remove_studied_piece(current_user.id, piece_id)
    if removed:
        flash("Piece removed from studied list.", "success")
    else:
        flash("Piece not found.", "error")
    return redirect(url_for('studied'))


if __name__ == '__main__':
    app.run(debug=True)