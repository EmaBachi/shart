from wtforms import Form, SelectMultipleField


class CollaboratorsForm(Form):

    my_choices = []

    def push_appliers(self, appliers):

        del self.my_choices[:]

        for applier in appliers:
            a = (applier, applier)
            self.my_choices.append(a)
            print(self.my_choices)

    appliers = SelectMultipleField(choices=my_choices)
