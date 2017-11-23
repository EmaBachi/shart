# External import
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging, send_from_directory
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
import datetime
import os


# Internal import
from RegisterForm import RegisterForm
from ArticleForm import ArticleForm
from CommentForm import CommentForm
from ContestForm import ContestForm
from ChangePasswordForm import ChangePasswordForm
from ChangeDescriptionForm import ChangeDescriptionForm


# Instantiate application object
app = Flask(__name__)

# Path to uploaded exclusive content
UPLOAD_FOLDER_VIDEO = '/home/emanuele/Scrivania/Shart_Contents/videos'

UPLOAD_FOLDER_IMAGE = '/home/emanuele/Scrivania/Shart_Contents/images'
app.config["UPLOAD_FOLDER_VIDEO"] = UPLOAD_FOLDER_VIDEO
app.config["UPLOAD_FOLDER_IMAGE"] = UPLOAD_FOLDER_IMAGE


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
        type = form.type.data
        app.logger.info(type)
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
                                  'type': type,
                                  'date_of_birth': date_of_birth,
                                  'country': country,
                                  'email': email,
                                  'password': password,
                                  'adm': False})

            # Using flash to print messages
            flash('You are now registered and can log in', 'success')

            # Redirecting user to home page
            return redirect(url_for('index'))

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


# ---!!! Starting from that point we have the programming part related to the blog !!!---


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
        flash('No article found', 'danger')
        return render_template('blog.html')


# Custom function that retrieves all tha articles from DB
def find_all_articles():
    articles = mongo.db.article.find()
    return articles


# Route for a single article
@app.route('/article/<string:title>', methods=['POST', 'GET'])
def article(title):
    form = CommentForm(request.form)

    # Retrieving article from db
    article = mongo.db.article.find_one({'title': title})

    if request.method == 'POST' and form.validate():
        comment_body = form.comment_body.data
        comment_author = session['username']
        date_mongo = str(datetime.date.today())

        # Calling a custom function to add the comment
        add_comment(article, comment_body, comment_author, date_mongo)

        return redirect(url_for("article", title=article['title']))

    return render_template('article.html', article=article, form=form, comments=article['comments'])


# Custom function to add a comment to an article
def add_comment(article, comment_body, comment_author, date_mongo):

    # MongoDB query to push an item into an array
    mongo.db.article.update({'title': article['title']},
                            {'$push': {"comments": {"author": comment_author,
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

        # MongoDB query to insert a new article
        mongo.db.article.insert({
            'title': title,
            'body': body,
            'author': author,
            'date': date_mongo,
            'comments': []
        })

        flash('Article created', 'success')

        # Redirecting user to the blog page
        return redirect(url_for('blog'))

    return render_template('add_article.html', form=form)


# Route for editing an article
@app.route('/edit_article/<string:title>', methods=['POST', 'GET'])
def edit_article(title):
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        date_mongo = str(datetime.date.today())

        # MongoDB query to modify the body of the article
        mongo.db.article.update({"title": title},
                                {'$set':   {"body": body,
                                            "author": author,
                                            "date": date_mongo}})

        flash('article edited', 'success')

        return redirect(url_for('blog'))

    else:
        article = mongo.db.article.find_one({'title': title})

        form.title.data = article['title']
        form.body.data = article['body']

        return render_template('edit_article.html', form=form)


# Route for deleting an article
@app.route('/delete_article/<string:title>', methods=['GET'])
def delete_article(title):

    # MongoDB query to delete an article starting from its title
    mongo.db.article.remove({"title": title})

    flash('Article deleted', 'success')

    # Redirecting user to the blog page
    return redirect(url_for('blog'))


# ---!!! Blog development completed !!!---


# ---!!! Starting from that point we have the programming part related to contests !!!---


# Route for All competitions
@app.route('/competitions')
def competitions():

    # Checking how many contests there are in db
    result = mongo.db.contest.find().count()

    if result > 0:
        # Fetching all contests
        contests = find_all_contests()
        today = datetime.date.today().strftime("%m/%d/%Y")
        app.logger.info(today)
        return render_template('competitions.html', contests=contests, today=today)
    else:
        flash('No contest found', 'danger')
        return render_template('competitions.html')


# Custom function to retrieve contests from db
def find_all_contests():
    contests = mongo.db.contest.find()
    return contests


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
            date_mongo = str(datetime.date.today())

            add_comment_contest(contest, comment_body, comment_author, date_mongo)

            return redirect(url_for('contest', title=contest['title']))

        return render_template('contest.html', contest=contest, form=form, comments=comments)


def add_comment_contest(contest, comment_body, comment_author, date_mongo):

    mongo.db.contest.update({'title': contest['title']},
                            {'$push':   {"comments":
                                                {"author": comment_author,
                                                "body": comment_body,
                                                "date": date_mongo}}})
    return


# Route for adding a contest
@app.route('/add_contest', methods=['POST', 'GET'])
def add_contest():
    form = ContestForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']
        enroll_deadline = form.enroll_deadline.data.strftime("%m/%d/%Y")
        presentation_deadline = form.presentation_deadline.data.strftime("%m/%d/%Y")
        type = form.type.data

        mongo.db.contest.insert({
            'title': title,
            'body': body,
            'author': author,
            'enroll_deadline': enroll_deadline,
            'presentation_deadline': presentation_deadline,
            'type': type,
            'comments': []
        })

        flash('Contest created', 'success')

        return redirect(url_for('competitions'))

    return render_template('add_contest.html', form=form)


# Route for editing a contest
@app.route('/edit_contest/<string:title>', methods=['POST', 'GET'])
def edit_contest(title):
    form = ContestForm(request.form)

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        author = session['username']
        date_mongo = str(datetime.date.today())

        # MongoDB query to modify an article
        mongo.db.contest.update({"title": title},
                                {'$set':
                                     {"body": body,
                                      "author": author,
                                      "date": date_mongo}})

        flash('Contest edited', 'success')

        # Redirecting user to the contests' main page
        return redirect(url_for('competitions'))
    else:
        # Retrieving contest from db
        contest = mongo.db.contest.find_one({'title': title})

        # Filling form fields with data from db
        form.title.data = contest['title']
        form.body.data = contest['body']

        return render_template('edit_contest.html', form=form)


# Route for deleting a contest
@app.route('/delete_contest/<string:title>', methods=['GET'])
def delete_contest(title):

    mongo.db.contest.remove({"title": title})

    flash('Contest deleted', 'success')

    return redirect(url_for('competitions'))


# ---!!! Contests development completed !!!---


# ---!!! Starting from that point we have the programming part related to exclusive contents !!!---

# Route for exclusive contents
@app.route('/exclusive_contents')
def exclusive_contents():
    return


# Route for add some exclusive material
@app.route('/add_exclusive_content', methods=['GET', 'POST'])
def add_exclusive_content():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return
        else:
            path = os.path.join(app.config['UPLOAD_FOLDER_VIDEO'],file.filename)
            description=request.form['description']
            video_name=request.form['video_name']
            mongo.db.exclusive_videos.insert({
                'path': path,
                'file_name': file.filename,
                'description': description,
                'video_name': video_name
            })

            # to save the path in the folder
            file.save(path)
            return redirect(url_for('video_gallery'))

    return render_template("upload_video.html")


# Route for displaying a single video
@app.route('/video/<video_name>')
def video(video_name):
    path = mongo.db.exclusive_videos.find_one({'file_name': video_name})
    head, tail = os.path.split(path["path"])
    return send_from_directory(head, video_name)


# Route for the videogallery
@app.route('/video_gallery')
def video_gallery():
    videos = mongo.db.exclusive_videos.find()

    return render_template('video_gallery.html', videos=videos)


# ---!!! Exclusive contents development completed !!!---


# ---!!! Profile developing !!!---

# Route for the profile
@app.route('/profile')
def profile():
    username = session['username']
    user = mongo.db.user.find_one({'username': username})
    print(user)
    return render_template('account_profile.html', user=user)


# Route for uploading profile image
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return
        else:
            path = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'],file.filename)
            username = session['username']
            user = mongo.db.user.find_one({'username':username})
            mongo.db.user.update({"username": username},
                                    {'$set':
                                         {
                                            'path': path,
                                            'image_name': file.filename}})


            # to save the path in the folder
            file.save(path)
            print(path)
            return redirect(url_for('profile'))

    return render_template("upload_image.html")


@app.route('/<image_name>')
def image(image_name):
    return send_from_directory(UPLOAD_FOLDER_IMAGE, image_name)


# Route to change the password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm(request.form)

    if request.method == "POST":
        username = session['username']
        user = mongo.db.user.find_one({'username': username})
        if form.new_password.data == '':
            flash('No new password', 'danger')
            return redirect(request.url)
        if sha256_crypt.verify(form.old_password.data, user['password']):
            password = sha256_crypt.encrypt(str(form.new_password.data))
            if password == '':
                flash('Error: you have to insert a new password', 'danger')
                return
            else:
                flash('Password successfully changed', 'success')
                username = session['username']
                mongo.db.user.update({"username": username},
                                        {'$set':
                                             {
                                                'password': password}})
            return render_template("account_profile.html", user=user)
        else:
            flash('Your old password does not match', 'danger')
            return redirect(request.url)

    return render_template("change_password.html", form=form)


# Route for displaying images
@app.route('/display_image')
def display_image():
    username = session['username']
    user = mongo.db.user.find_one({'username': username})
    image = user.path
    return render_template('account_profile.html', image=image)


# Route for change the user's description
@app.route('/change_description', methods=['GET', 'POST'])
def change_description():
    form = ChangeDescriptionForm(request.form)

    username = session['username']

    if request.method == 'POST':

        description = form.description.data

        mongo.db.user.update({'username': username}, {'$set': {
            'description': description
        }})

        return redirect(url_for('profile'))

    user = mongo.db.user.find_one({'username': username})

    try:
        description = user['description']
        form.description.data = description
    except KeyError:
        form.description.data = ''

    return render_template('change_description.html', form=form)


# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
