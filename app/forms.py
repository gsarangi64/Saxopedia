from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional


class UserForm(FlaskForm):
    uname = StringField("Username", validators=[DataRequired()])
    pw = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    uname = StringField("Username", validators=[DataRequired()])
    pw = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProgramForm(FlaskForm):
    name = StringField("Program Name", validators=[DataRequired()])
    submit = SubmitField("Create Program")


class AddPieceForm(FlaskForm):
    """Hidden fields carry piece data from the repertoire page."""
    piece_title = HiddenField(validators=[DataRequired()])
    composer = HiddenField()
    year = HiddenField()
    instrumentation = HiddenField()
    program_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Add")


class StudiedPieceForm(FlaskForm):
    """Hidden fields carry piece data; notes is optional."""
    piece_title = HiddenField(validators=[DataRequired()])
    composer = HiddenField()
    year = HiddenField()
    instrumentation = HiddenField()
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Mark as Studied")
