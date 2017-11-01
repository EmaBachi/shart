# External import
from flask import Flask, render_template, request

# Internal import
from RegisterForm import RegisterForm

# Instantiate application object
app = Flask(__name__)


# Route for home
@app.route('/')
def index():
    return render_template('home.html')


# Route for register a new user. Register endpoint can be reached by GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    return render_template('register.html', form=form)


# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
