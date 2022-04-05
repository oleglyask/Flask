
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField(label='remember_me')
    submit = SubmitField("Submit")

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=64)])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores',
        )])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password_confirm', message='Passwords do not match.' #Equalto() the field 'password_confirm'
        )])
    password_confirm = PasswordField('Password (confirm):',
                                     validators=[DataRequired()])
    submit = SubmitField("Register")

    # applies to any FlaskForm method that starts with validate_, where the next part of the name is the field that is validated
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Sorry! Username already in use.')