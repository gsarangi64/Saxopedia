#!usr/bin/env python3
from flask import Flask, render_template, flash, redirect, url_for
from services import load_repertoire, fetch_composer

#start of registration stuff

import os
from flask import Flask, render_template
from flask_login import UserMixin
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32) 

#forms
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length

#database stuff
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#password stuff
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    #Should include user playlist here
    
    @property
    def password(self):
        raise AttributeError("nah")
    
    @password.setter
    def password(self, pw):
        self.password_hash = generate_password_hash(pw)
    
    def verify_password(self, pw):
        return check_password_hash(self.password_hash, pw)

with app.app_context():
    db.create_all()  


class UserForm(FlaskForm):
    uname = StringField("Username: ", validators = [DataRequired()])
    pw = PasswordField("Password: ", validators = [DataRequired()])
    submit = SubmitField("Register")

    
def createUser(uname, pw):
    u = User.query.filter_by(uname=uname).first()
    if(u == None):
        user = User(uname=uname, password=pw)
        db.session.add(user)
        db.session.commit()
        return True
    else:
        return False

@app.route("/register", methods=['GET','POST'])
def register():
    form = UserForm()
    
    if(form.validate_on_submit()):
        uname = form.uname.data
        pw = form.pw.data
        created = createUser(uname, pw)
        if(created):
            flash("Registered Successfully!")
        else:
            flash("User already exists with username " + uname)
        return redirect(url_for('index'))
    
    return render_template("register.html", form = form)
    
#end of registration stuff    


#routes
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


if __name__ == '__main__':
    app.run(debug=True)