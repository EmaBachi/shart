from wtforms import TextAreaField, Form, validators


class CommentForm(Form):
    comment_body = TextAreaField('Leave a Comment:', [validators.Length(min=1, max=250)])