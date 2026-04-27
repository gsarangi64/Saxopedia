from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    programs = db.relationship("Program", backref="user", lazy="dynamic")
    studied_pieces = db.relationship("StudiedPiece", backref="user", lazy="dynamic")

    @property
    def password(self):
        raise AttributeError("nah")

    @password.setter
    def password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def verify_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Program(db.Model):
    __tablename__ = "programs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pieces = db.relationship("ProgramPiece", backref="program", lazy="dynamic", cascade="all, delete-orphan")

    # Unique per user, not globally
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_program_user_name"),
    )


class ProgramPiece(db.Model):
    """Join table linking a piece (by title) to a Program."""
    __tablename__ = "program_pieces"

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    piece_title = db.Column(db.String(128), nullable=False)
    composer = db.Column(db.String(128))
    year = db.Column(db.String(16))
    instrumentation = db.Column(db.String(256))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # No duplicate pieces within the same program
    __table_args__ = (
        db.UniqueConstraint("program_id", "piece_title", name="uq_program_piece"),
    )


class StudiedPiece(db.Model):
    """Tracks pieces a user has studied/performed."""
    __tablename__ = "studied_pieces"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    piece_title = db.Column(db.String(128), nullable=False)
    composer = db.Column(db.String(128))
    year = db.Column(db.String(16))
    instrumentation = db.Column(db.String(256))
    notes = db.Column(db.Text, default="")
    studied_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One entry per piece per user
    __table_args__ = (
        db.UniqueConstraint("user_id", "piece_title", name="uq_studied_user_piece"),
    )


# --- Helper functions ---

def create_user(uname, pw):
    u = User.query.filter_by(uname=uname).first()
    if u is None:
        user = User(uname=uname, password=pw)
        db.session.add(user)
        db.session.commit()
        return True
    return False


def create_program(name, user_id):
    existing = Program.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        return None, "You already have a program named '{}'".format(name)
    program = Program(name=name, user_id=user_id)
    db.session.add(program)
    db.session.commit()
    return program, None


def add_piece_to_program(program_id, piece_title, composer, year, instrumentation):
    existing = ProgramPiece.query.filter_by(program_id=program_id, piece_title=piece_title).first()
    if existing:
        return False, "Piece already in this program"
    pp = ProgramPiece(
        program_id=program_id,
        piece_title=piece_title,
        composer=composer,
        year=str(year) if year else "",
        instrumentation=instrumentation or ""
    )
    db.session.add(pp)
    db.session.commit()
    return True, None


def remove_piece_from_program(program_id, piece_id):
    pp = ProgramPiece.query.filter_by(id=piece_id, program_id=program_id).first()
    if pp:
        db.session.delete(pp)
        db.session.commit()
        return True
    return False


def mark_piece_studied(user_id, piece_title, composer, year, instrumentation, notes=""):
    existing = StudiedPiece.query.filter_by(user_id=user_id, piece_title=piece_title).first()
    if existing:
        return False, "Already in your studied list"
    sp = StudiedPiece(
        user_id=user_id,
        piece_title=piece_title,
        composer=composer,
        year=str(year) if year else "",
        instrumentation=instrumentation or "",
        notes=notes
    )
    db.session.add(sp)
    db.session.commit()
    return True, None


def remove_studied_piece(user_id, piece_id):
    sp = StudiedPiece.query.filter_by(id=piece_id, user_id=user_id).first()
    if sp:
        db.session.delete(sp)
        db.session.commit()
        return True
    return False
