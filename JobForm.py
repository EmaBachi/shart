from wtforms import Form, StringField, TextAreaField, validators, SelectField


class JobForm(Form):

    title = StringField('title', [
        validators.DataRequired(),
        validators.Length(min=2, max=20)
    ])

    location = StringField('location', [
        validators.DataRequired(),
        validators.Length(min=2, max=20)
    ])

    description = TextAreaField('description')

    companyname = StringField('company name')

    jobtype = SelectField('Select the job type:', choices=[('Part Time', 'Part Time'),
                                                    ('Full Time', 'Full Time'),
                                                     ('Contract', 'Contract')])
