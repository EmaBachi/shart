from wtforms import Form, StringField, TextAreaField, validators, SelectMultipleField, DateField, SelectField, IntegerField, PasswordField


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=30)])
    body = TextAreaField('Body')


class ChangeDescriptionForm(Form):
    description = StringField('Bio', [
        validators.DataRequired(),
        validators.Length(min=1, max=200)
    ])


class ChangePasswordForm(Form):
    old_password = StringField('Old Password', [validators.DataRequired()])
    new_password = StringField('New Password', [validators.DataRequired()])


class CollaboratorsForm(Form):

    my_choices = []

    def push_appliers(self, appliers):

        del self.my_choices[:]

        for applier in appliers:
            a = (applier, applier)
            self.my_choices.append(a)
            print(self.my_choices)

    appliers = SelectMultipleField(choices=my_choices)


class CommentForm(Form):
    comment_body = TextAreaField('Leave a Comment:', [validators.Length(min=1, max=250)])


class ContestForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=30)])
    enroll_deadline = DateField('Enroll Deadline', format="%m/%d/%Y")
    presentation_deadline = DateField('Presentation Deadline', format='%m/%d/%Y')
    type = SelectField('Contest for:', choices=[('Architect', 'Architect'),
                                                ('Designer', 'Designer'),
                                                ('Writer', 'Writer')])
    body = TextAreaField('Body')


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

    type = SelectField('You want to join our community as:', choices=[
                                                    ('Artist', 'Artist'),
                                                     ('Gallery Owner', 'Gallery Owner')])

    date_of_birth = DateField('Date of Birth', format="%m/%d/%Y")

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