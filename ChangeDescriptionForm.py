from wtforms import Form, StringField, validators


class ChangeDescriptionForm(Form):
    description = StringField('Bio', [
        validators.DataRequired(),
        validators.Length(min=1, max=200)
    ])

