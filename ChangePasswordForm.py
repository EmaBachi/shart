from wtforms import Form, StringField, validators


class ChangePasswordForm(Form):
    old_password = StringField('Old Password', [validators.DataRequired()])
    new_password = StringField('New Password', [validators.DataRequired()])
