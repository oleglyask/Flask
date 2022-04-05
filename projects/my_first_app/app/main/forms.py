from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired

# create a Form class called NameForm that extends the FlaskForm class
class NameForm(FlaskForm):
    name = StringField("Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# birthday form
class BirthdayForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    submit = SubmitField('Submit')