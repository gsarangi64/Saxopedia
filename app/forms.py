from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    uname = StringField("Username: ", validators=[DataRequired()])
    pw = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    uname = StringField("Username: ", validators=[DataRequired()])
    pw = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Login")

class ProgramForm(FlaskForm):
    name = StringField("Name of Program: ", validators=[DataRequired()])
    submit = SubmitField("Submit")
