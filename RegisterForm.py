# Registration form class using wtforms
from wtforms import Form, StringField, PasswordField, DateField, validators
# from wtforms.fields.html5 import DateField


class RegisterForm(Form):

    first_name = StringField('First Name', [
        validators.DataRequired(),
        validators.Length(min=2, max=20)
    ])

    surname = StringField('Surname', [
        validators.DataRequired(),
        validators.Length(min=2, max=20)
    ])

    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=20)
    ])

    # date_of_birth = DateField('Date of Birth', [validators.DataRequired()])

    country = StringField('Country', [validators.DataRequired()])

    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)
    ])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password do not match")

    ])

    confirm = PasswordField('Confirm Password')
