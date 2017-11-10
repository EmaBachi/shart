# External import
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
import datetime


# Internal import
from RegisterForm import RegisterForm
from ArticleForm import ArticleForm
from CommentForm import CommentForm

from ContestForm import ContestForm

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
        date_of_birth = form.date_of_birth.data.strftime("%m/%d/%Y")
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
                                  'date_of_birth': date_of_birth,
                                  'country': country,
                                  'email': email,
                                  'password': password,
                                  'adm': False})

            # Using flash to print messages
            flash('You are now registered and can log in', 'success')

            # Redirecting user to home page
            return render_template('home.html')

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
                if user['adm'] == True:
                    session['adm'] = True
                else:
                    session['adm'] = False

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



# Route for About
@app.route('/about')
def about():
    return render_template('about.html')


# Route for Blog
@app.route('/blog')
def blog():

    # Checking how many articles there are in db
    result = mongo.db.article.find().count()

    if result > 0:
        # Fetching all articles
        articles = find_all_articles()
        return render_template('blog.html', articles=articles)
    else:
        return render_template('blog.html')


# Route foa a single article

@app.route('/article/<string:title>', methods=['POST', 'GET'])
def article(title):
    form = CommentForm(request.form)

    # Retrieving article from db
    article = mongo.db.article.find_one({'title': title})

    comments = article['comments']

    if request.method == 'POST' and form.validate():
        comment_body = form.comment_body.data
        comment_author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)

        add_comment(article, comment_body, comment_author, date_mongo)

        # Retrieving article from db
        article = mongo.db.article.find_one({'title': title})

        comments = article['comments']

        form.comment_body.data = ""

        return render_template('article.html', article=article, form=form, comments=comments)

    return render_template('article.html', article=article, form=form, comments=comments)


def add_comment(article, comment_body, comment_author, date_mongo):

    mongo.db.article.update({'title': article['title']}, {'$push': {"comments":
                                                                        {"author": comment_author,
                                                                         "body": comment_body,
                                                                         "date": date_mongo}}})

    return

# Route for adding an article
@app.route('/add_article', methods=['POST', 'GET'])
def add_article():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)

        mongo.db.article.insert({
            'title': title,
            'body': body,
            'author': author,
            'date': date_mongo,
            'comments': []
        })

        flash('Article created', 'success')

        articles = find_all_articles()

        return render_template('blog.html', articles=articles)

    return render_template('add_article.html', form=form)

def find_all_articles():
    articles = mongo.db.article.find()
    return articles


#route for editing an article
@app.route('/editarticle.html/<string:title>', methods=['POST', 'GET'])
def edit_article(title):
    # Retrieving article from db
    article = mongo.db.article.find_one({'title': title})

    form = ArticleForm(request.form)
    form.title.data= article['title']
    form.body.data= article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)

        mongo.db.article.update({"title": title}, {'$set': { "body": body, "author": author, "date": date_mongo}})

        flash('article edited', 'success')

        articles= find_all_articles()

        return render_template('blog.html', articles=articles)

    return render_template('editarticle.html', form=form)


# Route for All competitions
@app.route('/contest')
def competitions():

    # Checking how many contests there are in db
    result = mongo.db.contest.find().count()

    if result > 0:
        # Fetching all contests
        contests = find_all_contests()
        return render_template('competitions.html', contests=contests)
    else:
        flash('No contest found','danger')
        return render_template('competitions.html')


# Route for a single contest
@app.route('/contest/<string:title>', methods=['POST', 'GET'])
def contest(title):
        form = CommentForm(request.form)

        # Retrieving contest from db
        contest = mongo.db.contest.find_one({'title': title})

        comments = contest['comments']

        if request.method == 'POST' and form.validate():
            comment_body = form.comment_body.data
            comment_author = session['username']
            date_python = datetime.date.today()
            date_mongo = str(date_python)

            add_comment_contest(contest, comment_body, comment_author, date_mongo)

            # Retrieving contest from db
            contest = mongo.db.contest.find_one({'title': title})

            comments = contest['comments']

            form.comment_body.data = ""

            return render_template('contest.html', contest=contest, form=form, comments=comments)

        return render_template('contest.html', contest=contest, form=form, comments=comments)

def add_comment_contest(contest, comment_body, comment_author, date_mongo):

    mongo.db.contest.update({'title': contest['title']}, {'$push': {"comments":
                                                                            {"author": comment_author,
                                                                             "body": comment_body,
                                                                             "date": date_mongo}}})

    return


#route for adding a contest
@app.route('/add_contest', methods=['POST', 'GET'])
def add_contest():
    form = ContestForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        #type = form.type.data
        author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)

        mongo.db.contest.insert({
            'title': title,
            'body': body,
           # 'type': type,
            'author': author,
            'date': date_mongo,
            'comments': []
        })

        flash('Contest created', 'success')

        contests = find_all_contests()

        return render_template('competitions.html', contests=contests)

    return render_template('add_contest.html', form=form)


def find_all_contests():
    contests = mongo.db.contest.find()
    return contests


#route for editing a contest
@app.route('/editcontest.html/<string:title>', methods=['POST', 'GET'])
def edit_contest(title):
    # Retrieving contest from db
    contest = mongo.db.contest.find_one({'title': title})

    form = ContestForm(request.form)
    form.title.data= contest['title']
    form.body.data= contest['body']
    #form.type.data= contest['type']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)
        #type = request.form['type']


        mongo.db.contest.update({"title": title}, {'$set': { "body": body, "author": author, "date": date_mongo}})

        flash('Contest edited', 'success')

        contests = find_all_contests()

        return render_template('competitions.html', contests=contests)

    return render_template('editcontest.html', form=form)


#route for deleting a contest
@app.route('/delete_contest.html/<string:title>', methods=['POST', 'GET'])
def delete_contest(title):
    # Retrieving contest from db
    contest = mongo.db.contest.find_one({'title': title})

    form = ContestForm(request.form)
    form.title.data= contest['title']
    form.body.data= contest['body']
    #form.type.data= contest['type']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        date_python = datetime.date.today()
        date_mongo = str(date_python)
        #type = request.form['type']

        mongo.db.contest.update({"title": title}, {'$set': { "body": body, "author": author, "date": date_mongo}})

        flash('Contest edited', 'success')

        contests = find_all_contests()

        return render_template('competitions.html', contests=contests)

    return render_template('editcontest.html', form=form)


# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
