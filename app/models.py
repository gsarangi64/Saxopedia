from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()



class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    programs = db.relationship("Program", backref="user")

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
    name = db.Column(db.String(64), unique=True, index=True)
    piece1 = db.Column(db.String(64))
    piece2 = db.Column(db.String(64))
    piece3 = db.Column(db.String(64))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    
def initializeProgram(name):
    program = Program(name=name, piece1="",piece2="",piece3="",user_id = current_user.id)
    db.session.add(program)
    db.session.commit()
    

def createUser(uname, pw):
    u = User.query.filter_by(uname=uname).first()
    if u is None:
        user = User(uname=uname, password=pw)
        db.session.add(user)
        db.session.commit()
        return True
    return False