from wtforms import Form, StringField, TextAreaField, validators


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=30)])
    body = TextAreaField('Body')

