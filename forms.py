from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, ValidationError


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

class EntryForm(FlaskForm):

    title = StringField(
        'Title',
        validators=[
            DataRequired()
        ]
    )

    date = DateTimeField(
        'Date',
        format='%d-%m-%Y',
        validators=[
            DataRequired()
        ]
    )

    time_spent = StringField(
        'Time Spent',
        validators=[
            DataRequired()
        ]
    )

    what_i_learned = TextAreaField()
    sources_to_remember = TextAreaField()

    tags = StringField('Tags. Seperate them with a ","')
