from flask_wtf import FlaskForm
from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, IntegerField, SubmitField,HiddenField, ValidationError
from wtforms.fields import EmailField , PasswordField
from wtforms.validators import Email, DataRequired, NumberRange, Length
from activities import load_tours


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
    user_name = StringField('Your Name:', validators=[DataRequired()], render_kw={"readonly": True})
    user_email = EmailField('Your Email:', validators=[DataRequired(), Email()], render_kw={"readonly": True})
    seats = IntegerField('Number of Seats:', validators=[
        DataRequired(),
        NumberRange(min=1, message="Must purchase at least 1 seat")
    ])
    submit = SubmitField('Purchase')

def unique_tour_name(form, field):
    tours = load_tours()  # Assume this returns a list of existing tours
    for tour in tours:
        tourname = tour.get_name()
        if tourname.lower() == field.data.lower():
            raise ValidationError(f"The tour name '{field.data}' already exists. Please choose a different name.")

class AddTourForm(FlaskForm):
    event_name = StringField(
        "Tour Name",
        validators=[
            DataRequired(message="Tour name is required."),
            Length(max=100, message="Tour name cannot exceed 100 characters."),
            unique_tour_name,
        ],
    )
    event_desc = StringField(
        "Tour Description",
        validators=[
            DataRequired(message="Tour description is required."),
            Length(max=200, message="Description cannot exceed 200 characters."),
        ],
    )
    country = StringField(
        "Country",
        validators=[
            DataRequired(message="Country is required."),
            Length(max=50, message="Country name cannot exceed 50 characters."),
        ],
    )
    submit = SubmitField("Add Tour")


class EditProfileForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    number = StringField('Phone Number', [validators.Length(min=8, max=8), validators.DataRequired()])
    submit = SubmitField('Update Profile')

class SearchTourForm(FlaskForm):
    country = StringField(
        "Search by Country",
        validators=[DataRequired(message="Please enter a country name.")],
        render_kw={"placeholder": "Eg. Singapore", "oninput": "this.value = this.value.charAt(0).toUpperCase() + this.value.slice(1).toLowerCase()"}
    )
    submit = SubmitField("Search")

class PassengerForm(FlaskForm):
    name = StringField(
        "Passenger Full Name",
        validators=[DataRequired(), Length(max=100, message="Name cannot exceed 100 characters.")]
    )
    age = IntegerField(
        "Passenger Age",
        validators=[DataRequired(), NumberRange(min=0, message="Age must be a valid number.")]
    )
    passport_number = StringField(
        "Passport Number",
        validators=[DataRequired(), Length(min=6, max=9, message="Enter a valid passport number.")]
    )
    contact_number = StringField('Contact Number', [validators.Length(min=8, max=8), validators.DataRequired()])
    email = EmailField("Email",validators=[DataRequired(), Email(message="Enter a valid email address.")])
    submit = SubmitField("Save Passenger")


