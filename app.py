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
from JobForm import JobForm
from ProjectForm import ProjectForm
from CollaboratorsForm import CollaboratorsForm

# Instantiate application object
app = Flask(__name__)


# Path to uploaded exclusive content
UPLOAD_FOLDER_VIDEO = 'C:\Users\Alessia\Desktop\dvideo'

# Path to profile images
UPLOAD_FOLDER_IMAGE = '/home/emanuele/Scrivania/Shart_Contents/images'

# Path to contest folder
UPLOAD_FOLDER_CONTEST = '/home/emanuele/Scrivania/Shart_Contents/contests'

# Application Configuration
app.config["UPLOAD_FOLDER_VIDEO"] = UPLOAD_FOLDER_VIDEO
app.config["UPLOAD_FOLDER_IMAGE"] = UPLOAD_FOLDER_IMAGE
app.config["UPLOAD_FOLDER_CONTEST"] = UPLOAD_FOLDER_CONTEST
app.config["USE_X_SENDFILE "] = True


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

                if 'type' in user.keys() and user['type'] == 'Gallery Owner':
                    session['scout'] = True
                    session['artist'] = False
                elif 'type' in user.keys() and user['type'] == 'Artist':
                    session['artist'] = True
                    session['scout'] = False
                else:
                    session['scout'] = False
                    session['artist'] = False

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

        files = contest['files']

        images = []

        for file in files:
            images.append(file['file_name'])

        not_allowed_to_upload = False

        for image in images:
            list = image.split('.')
            username_candidate = list[0]
            if 'username' in session and session['username'] == username_candidate:
                not_allowed_to_upload = True
                break

        today = datetime.date.today().strftime("%m/%d/%Y")

        if request.method == 'POST' and form.validate():
            comment_body = form.comment_body.data
            comment_author = session['username']
            date_mongo = str(datetime.date.today())

            add_comment_contest(contest, comment_body, comment_author, date_mongo)

            return redirect(url_for('contest', title=contest['title']))

        return render_template('contest.html', contest=contest, form=form, comments=comments,
                               today=today, files=files, not_allowed_to_upload=not_allowed_to_upload)


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

        # Storing the contest in db
        mongo.db.contest.insert({
            'title': title,
            'body': body,
            'author': author,
            'enroll_deadline': enroll_deadline,
            'presentation_deadline': presentation_deadline,
            'type': type,
            'folder': title,
            'files': [],
            'competitors': [],
            'comments': []
        })

        # Create a directory in the server to store all the projects related to the contest
        create_directory_for_contest(title)

        flash('Contest created', 'success')

        return redirect(url_for('competitions'))

    return render_template('add_contest.html', form=form)


# Function for create a new directory in the contest path
def create_directory_for_contest(title):
    directory = UPLOAD_FOLDER_CONTEST+"/"+title
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


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


# Route for joining a contest
@app.route('/join_contest/<string:title>')
def join_contest(title):

    mongo.db.contest.update({"title": title}, {'$push': {'competitors': session['username']}})

    flash('You have joined the contest. Now work hard to achieve the VICTORY', 'success')

    return redirect(url_for('competitions'))


# Route for upload a project in the contest folder
@app.route('/upload_project_contest/<string:title>', methods=['GET', 'POST'])
def upload_project_contest(title):

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        else:
            parts = file.filename.split('.')
            extension = parts[1]
            image_to_save = session['username']+"."+extension

            # Storing file in contest document with some specific informations
            mongo.db.contest.update({'title': title},
                                    {'$push':
                                         {'files':
                                              { 'user': session['username'],
                                                'primary_folder': UPLOAD_FOLDER_CONTEST,
                                                'secondary_folder': title,
                                                'file_name': image_to_save,
                                                'like': 0,
                                                'unlike': 0
                                                }
                                          }
                                     })

            path = os.path.join(UPLOAD_FOLDER_CONTEST+"/"+title, image_to_save)

            # to save the path in the folder
            file.save(path)

            flash('Project Uploaded. Cross your Fingers', 'success')

            return redirect(url_for('contest', title=title))

    return render_template('upload_project_contest.html')


@app.route('/image_contest/<string:title>/<string:file_name>')
def image_contest(title, file_name):
    return send_from_directory(UPLOAD_FOLDER_CONTEST+"/"+title, file_name)


@app.route('/user_contest')
def user_contest():
    username = session['username']

    contests = mongo.db.contest.find({'competitors': username})
    today = datetime.date.today().strftime("%m/%d/%Y")
    return render_template('competitions.html', contests=contests, today=today)


@app.route('/contest/<string:title>/<string:name>/like')
def like(title, name):

    mongo.db.contest.update({'title': title, 'files.file_name': name}, {'$inc': {'files.$.like': 1}})

    return redirect(url_for('contest', title=title))


@app.route('/contest/<string:title>/<string:name>/unlike')
def unlike(title, name):

    mongo.db.contest.update({'title': title, 'files.file_name': name}, {'$inc': {'files.$.unlike': 1}})

    return redirect(url_for('contest', title=title))


# ---!!! Contests development completed !!!---


# ---!!! Starting from that point we have the programming part related to exclusive contents !!!---


# Route for add some exclusive material
@app.route('/add_exclusive_content', methods=['GET', 'POST'])
def add_exclusive_content():
    if request.method == "POST":

        description = request.form['description']
        video_name = request.form['video_name']
        url_video = request.form['url_video']

        mongo.db.exclusive_videos.insert({
            'description': description,
            'video_name': video_name,
            'url_video': url_video
        })
        # to save the path in the folder
        return redirect(url_for('video_gallery'))

    return render_template("upload_video.html")


# Route for the video gallery
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

    contest_images = retrieve_images_contests(user['username'])

    return render_template('account_profile.html', user=user, contest_images=contest_images)


# Function for retrieving contests images
def retrieve_images_contests(username):

    query = mongo.db.contest.find({
        'files.user': username
    },
        {
            '_id': 0,
            'files': 1
        })

    images = []

    for item in query:
        for file in item['files']:
            images.append(file)

    return images


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


# ---!!! job section developing !!!---

@app.route('/add_job', methods=['GET','POST'])
def add_job():
    form = JobForm(request.form)

    if request.method == 'POST':
        title = form.title.data
        location = form.location.data
        app.logger.info(location)
        jobtype = form.jobtype.data
        companyname = form.companyname.data
        description = form.description.data
        author = session['username']

        app.logger.info(title)

        # MongoDB query to insert a new article
        mongo.db.job.insert({
            'title': title,
            'location': location,
            'author': author,
            'jobtype' : jobtype,
            'description' : description,
            'companyname' : companyname
        })

        flash('Job posted', 'success')

        # Redirecting user to the blog page
        return redirect(url_for('jobs'))

    return render_template("post_job.html",form=form)

# Route for displaying all jobs
@app.route('/jobs')
def jobs():
    # Checking how many jobs there are in db
    result = mongo.db.job.find().count()

    if result > 0:
        # Fetching all contests
        jobs = mongo.db.job.find()
        return render_template('jobs.html', jobs=jobs)
    else:
        flash('No job found', 'danger')
        return render_template('jobs.html')


# ---!!! Jobs section fully implemented !!!---

# ---!!! Share folder for projects !!!---

@app.route('/projects')
def projects():

    projects = mongo.db.project.find({})

    return render_template('projects.html', projects=projects)


@app.route('/user_projects')
def user_projects():

    projects = mongo.db.project.find({'$or': [{'author': session['username']}, {'collaborators': {'$in': [session['username']]}}]})

    return render_template('projects.html', projects=projects)


@app.route('/add_project', methods=['POST', 'GET'])
def add_project():

    form = ProjectForm(request.form)

    if request.method == 'POST':

        title = form.title.data
        description = form.description.data
        max_number = form.max_number.data
        app.logger.info(form.skills.data)
        skills = form.skills.data
        author = session['username']
        appliers = []
        collaborators = []
        status = 'WIP'

        mongo.db.project.insert({
            'title': title,
            'description': description,
            'author': author,
            'max_number': max_number,
            'skills': skills,
            'appliers': appliers,
            'collaborators': collaborators,
            'status': status
        })

        return redirect(url_for('projects'))

    return render_template('add_project.html', form=form)


@app.route('/join_project/<string:title>')
def join_project(title):

    mongo.db.project.update({'title': title}, {'$push': {'appliers': session['username']}})

    flash('You apply for the project', 'success')

    return redirect(url_for('projects'))


@app.route('/projects/<string:title>', methods=['POST', 'GET'])
def single_project(title):
    form = CollaboratorsForm(request.form)

    project = mongo.db.project.find_one({'title': title})

    app.logger.info(project)

    appliers = project['appliers']

    if request.method == 'POST':

        return redirect(url_for('home'))

    else:

        form.push_appliers(appliers)

        return render_template('single_project.html', project=project, form=form)



# Route for searching
# -----------!!!!!!! WE HAVE TO MAKE THE PROFILES VISIBLE!!!
@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        username = request.form['q']
        app.logger.info(username)

    return render_template("about.html")

# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)
