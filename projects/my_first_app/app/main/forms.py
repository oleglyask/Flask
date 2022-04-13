from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp
from ..models import User, Role

# allows the user to edit its profile
class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

# allows an administrator to edit anyone's profile
class AdminLevelEditProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores',
        )])
    confirmed = BooleanField("Confirmed")
    #coerce specifies what type the choice value should be return as (should match role in Model.py)
    # choices for the role field will be dynamically assigned in the view function
    role = SelectField("Role", coerce=int)
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        # role.id is the value that will get returned, role.name is the label that will apear on the form
        self.role.choices = [(role.id, role.name) for role in Role.query.all()]


    # checks to see that username is not used already
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() and field.data != self.user.username:
            raise ValidationError('Sorry! Username already in use.')
