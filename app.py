# External import
from flask import Flask, render_template, request, flash, redirect, url_for, session
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

        already_username = mongo.db.user.find({'username': username}).count()

        # Error message
        if already_username != 0:
            flash('Username already chosen', 'danger')
            return render_template('register.html', form=form)
        else:
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
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        username_candidate = request.form['username']
        password_candidate = request.form['password']

        # Retrieving data from mongodb
        user = mongo.db.user.find_one({'username': username_candidate})

        # Check if the username is correct
        try:
            len(user)

            password_user = user['password']

            # Check the password
            if sha256_crypt.verify(password_candidate, password_user):
                session['logged_in'] = True
                session['username'] = username_candidate

                flash('You are now logged in', 'success')
                return redirect(url_for("index"))

            else:
                error = "Invalid password"
                return render_template('login.html', error=error)

        except TypeError:
            error = "Invalid username"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session variable
    session.clear()

    flash('You are now logged off', 'success')

    return redirect(url_for('login'))


# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
