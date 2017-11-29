from wtforms import Form, StringField, validators, SelectMultipleField, IntegerField


class ProjectForm(Form):

    title = StringField('Title', [
        validators.DataRequired(),
        validators.Length(min=1, max=30)
    ])

    description = StringField('Description', [
        validators.DataRequired(),
        validators.Length(min=1, max=200)
    ])

    my_choices = [('Designer', 'Designer'), ('Architect', 'Architect')]

    skills = SelectMultipleField(choices=my_choices)

    max_number = IntegerField('Max Number of Collaborators', [validators.DataRequired()])

