# External import
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt


# Internal import
from RegisterForm import RegisterForm

# Instantiate application object
app = Flask(__name__)

# DB Configuration
app.config["MONGO1_DBNAME"] = 'shart'
mongo = PyMongo(app, config_prefix='MONGO1')


# Route for home
@app.route('/')
def index():
    return render_template('home.html')


# Route for register a new user. Register endpoint can be reached by GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    # Check whether the http method is POST and check form validation
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        surname = form.surname.data
        username = form.username.data
        # date_of_birth = form.date_of_birth.data
        country = form.country.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Commit
        mongo.db.user.insert({'first_name': first_name,
                              'surname': surname,
                              'username': username,
                              'country': country,
                              'email': email,
                              'password': password})

        # Using flash to print messages
        flash('You are now registered and can log in', 'success')

        # Redirecting user to home page
        return render_template('login.html')

    return render_template('register.html', form=form)


# User login
@app.route('/login')
def login():
    render_template('login.html')

# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
