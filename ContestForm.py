from wtforms import Form, StringField, TextAreaField, validators, DateField, SelectField


class ContestForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=30)])
    enroll_deadline = DateField('Enroll Deadline', format="%m/%d/%Y")
    presentation_deadline = DateField('Presentation Deadline', format='%m/%d/%Y')
    type = SelectField('Contest for:', choices=[('Choose an Option', 'Choose an Option'),
                                                                      ('Architect', 'Architect'),
                                                                      ('Designer', 'Designer'),
                                                                      ('Writer', 'Writer')])
    body = TextAreaField('Body')



