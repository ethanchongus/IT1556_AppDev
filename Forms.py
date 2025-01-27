from flask_wtf import FlaskForm
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, IntegerField, SubmitField
from wtforms.fields import EmailField , PasswordField
from wtforms.validators import Email, DataRequired, NumberRange

class CreateUserForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    membership = RadioField('Department', choices=[('C', 'Customer Support'), ('A', 'Admin'), ('I', 'IT Support')], default='A')
    remarks = TextAreaField('Remarks', [validators.Optional()])
    number = StringField("Phone Number", [validators.Length(min=8, max=8), validators.DataRequired()])
    email = EmailField("Email",[validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6), validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])


class CreateCustomerForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6), validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])
    number = StringField('Phone Number', [validators.Length(min=8, max=8), validators.DataRequired()])

class LoginForm(Form):
    email = StringField('Email', [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [validators.DataRequired()])

class TourPurchaseForm(FlaskForm):
    departure_date = SelectField('Select Departure Date:', validators=[DataRequired()])
    user_name = StringField('Your Name:', validators=[DataRequired()])
    user_email = EmailField('Your Email:', validators=[DataRequired(), Email()])
    seats = IntegerField('Number of Seats:', validators=[
        DataRequired(),
        NumberRange(min=1, message="Must purchase at least 1 seat")
    ])
    submit = SubmitField('Purchase')