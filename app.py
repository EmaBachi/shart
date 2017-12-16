# External import
from flask import Flask, render_template, request, flash, redirect, url_for, session, logging, send_from_directory
from flask_pymongo import PyMongo
import datetime
import os


# Internal import
from Form import RegisterForm, ArticleForm, CommentForm, ContestForm, ChangePasswordForm, ChangeDescriptionForm, JobForm, ProjectForm, CollaboratorsForm
from Services import UserService, ArticleService, ContestService, ExclusiveVideoService, JobService, ProjectService

# Instantiate application object
app = Flask(__name__)
app.config.from_object('config')


# Path to profile images
UPLOAD_FOLDER_IMAGE = '/home/emanuele/Scrivania/Shart_Contents/images'

# Path to contest folder
UPLOAD_FOLDER_CONTEST = '/home/emanuele/Scrivania/Shart_Contents/contests'

# Path to project folder
UPLOAD_FOLDER_PROJECT = '/home/emanuele/Scrivania/Shart_Contents/projects'


# Application Configuration
app.config["UPLOAD_FOLDER_IMAGE"] = UPLOAD_FOLDER_IMAGE
app.config["UPLOAD_FOLDER_CONTEST"] = UPLOAD_FOLDER_CONTEST
app.config["UPLOAD_FOLDER_PROJECT"] = UPLOAD_FOLDER_PROJECT


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
        date_of_birth = form.date_of_birth.data.strftime("%m/%d/%Y")
        country = form.country.data
        email = form.email.data
        password = form.password.data

        # Error message
        if not UserService.create_user(first_name, surname, username, date_of_birth,
                                        country, email, password, type):

            flash('Username already chosen', 'danger')
            return render_template('register.html', form=form)
        else:
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

        user = UserService.login(username_candidate, password_candidate)

        if user is not None:

            session['logged_in'] = True
            session['username'] = user.username

            session['adm'] = user.adm

            if user.type == 'Gallery Owner':
                session['scout'] = True
                session['artist'] = False
            elif user.type == 'Artist':
                session['scout'] = False
                session['artist'] = True
            else:
                session['scout'] = False
                session['artist'] = False

            flash('You are now logged in', 'success')
            return redirect(url_for("index"))

        else:

            error = "Invalid username or password"
            return render_template('login.html', error=error)

    else:
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

    articles = ArticleService.find_all_articles()

    if len(articles) > 0:
        # Fetching all articles
        return render_template('blog.html', articles=articles)
    else:
        flash('No article found', 'danger')
        return render_template('blog.html')


# Route for a single article
@app.route('/article/<string:title>', methods=['POST', 'GET'])
def article(title):
    form = CommentForm(request.form)

    # Retrieving article from db
    article = ArticleService.find_by_title(title)

    if request.method == 'POST' and form.validate():
        comment_body = form.comment_body.data
        comment_author = session['username']

        ArticleService.add_comment_to_article(article, comment_author, comment_body, datetime.date.today())

        return redirect(url_for("article", title=article.title))

    return render_template('article.html', article=article, form=form, comments=article.comments)


# Route for adding an article
@app.route('/add_article', methods=['POST', 'GET'])
def add_article():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']
        date_python = datetime.date.today()

        ArticleService.save(title, body, author, date_python)

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

        # MongoDB query to modify the body of the article
        ArticleService.edit(title, body, author, datetime.date.today())

        flash('article edited', 'success')

        return redirect(url_for('blog'))

    else:
        article = ArticleService.find_by_title(title)

        form.title.data = article.title
        form.body.data = article.body

        return render_template('edit_article.html', form=form)


# Route for deleting an article
@app.route('/delete_article/<string:title>', methods=['GET'])
def delete_article(title):

    ArticleService.remove(title)

    flash('Article deleted', 'success')

    # Redirecting user to the blog page
    return redirect(url_for('blog'))


# ---!!! Blog development completed !!!---


# ---!!! Starting from that point we have the programming part related to contests !!!---


# Route for All competitions
@app.route('/competitions')
def competitions():

    # Checking how many contests there are in db
    contests = ContestService.find_all_contests()

    if len(contests) > 0:
        # Fetching all contests
        today = datetime.date.today().strftime("%m/%d/%Y")
        return render_template('competitions.html', contests=contests, today=today)
    else:
        flash('No contest found', 'danger')
        return render_template('competitions.html')


# Route for a single contest
@app.route('/contest/<string:title>', methods=['POST', 'GET'])
def contest(title):
        form = CommentForm(request.form)

        # Retrieving contest from db
        contest = ContestService.find_by_title(title)

        comments = contest.comments

        files = contest.files_project

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

            ContestService.add_comment_to_contest(contest, comment_body, comment_author, datetime.date.today())

            return redirect(url_for('contest', title=contest.title))

        return render_template('contest.html', contest=contest, form=form, comments=comments,
                               today=today, files=files, not_allowed_to_upload=not_allowed_to_upload)


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

        ContestService.save(title, author, body, type, presentation_deadline, enroll_deadline)

        flash('Contest created', 'success')

        return redirect(url_for('competitions'))

    return render_template('add_contest.html', form=form)


# Route for editing a contest
@app.route('/edit_contest/<string:title>', methods=['POST', 'GET'])
def edit_contest(title):
    form = ContestForm(request.form)

    if request.method == 'POST':

        print("SONO ENTRATO DENTRO EDIT POST")
        title = request.form['title']
        body = request.form['body']
        author = session['username']

        ContestService.edit(title, body, author)

        flash('Contest edited', 'success')

        # Redirecting user to the contests' main page
        return redirect(url_for('competitions'))
    else:
        # Retrieving contest from db
        contest = ContestService.find_by_title(title)

        # Filling form fields with data from db
        form.title.data = contest.title
        form.body.data = contest.body

        return render_template('edit_contest.html', form=form)


# Route for deleting a contest
@app.route('/delete_contest/<string:title>', methods=['GET'])
def delete_contest(title):

    ContestService.remove(title)

    flash('Contest deleted', 'success')

    return redirect(url_for('competitions'))


# Route for joining a contest
@app.route('/join_contest/<string:title>')
def join_contest(title):

    ContestService.join_contest(title, session['username'])

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

            ContestService.upload_project_contest(session['username'], title, image_to_save, file)

            flash('Project Uploaded. Cross your Fingers', 'success')

            return redirect(url_for('contest', title=title))

    return render_template('upload_project_contest.html')


@app.route('/image_contest/<string:title>/<string:file_name>')
def image_contest(title, file_name):
    return ContestService.send_image(title, file_name)


@app.route('/user_contest')
def user_contest():
    contests = ContestService.find_contest_by_user(session['username'])
    today = datetime.date.today().strftime("%m/%d/%Y")
    return render_template('competitions.html', contests=contests, today=today)


@app.route('/contest/<string:title>/<string:name>/like')
def like(title, name):

    ContestService.like(title, name)

    return redirect(url_for('contest', title=title))


@app.route('/contest/<string:title>/<string:name>/unlike')
def unlike(title, name):

    ContestService.unlike(title, name)

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

        ExclusiveVideoService.save(description, video_name, url_video)

        return redirect(url_for('video_gallery'))

    return render_template("upload_video.html")


# Route for the video gallery
@app.route('/video_gallery')
def video_gallery():
    # Checking how many videos there are in db
    exclusive_videos = ExclusiveVideoService.find_all()
    if len(exclusive_videos) > 0:
        return render_template('video_gallery.html', videos=exclusive_videos)
    else:
        flash('No video found', 'danger')
        return render_template('video_gallery.html')


# Route for deleting a video
@app.route('/delete_video/<string:title>', methods=['GET'])
def delete_video(title):

    ExclusiveVideoService.remove(title)
    flash('Video deleted', 'success')
    return redirect(url_for('video_gallery'))

# ---!!! Exclusive contents development completed !!!---


# ---!!! Profile developing !!!---

# Route for the profile
@app.route('/profile/<string:username>')
def other_profile(username):
    user = mongo.db.user.find_one({'username': username})

    contest_images = retrieve_images_contests(user['username'])

    project_images = retrieve_images_projects(user['username'])

    return render_template('account_profile.html', user=user, contest_images=contest_images)

# Route for the profile
@app.route('/profile')
def profile():
    username = session['username']
    user = mongo.db.user.find_one({'username': username})

    contest_images = retrieve_images_contests(user['username'])

    project_images = retrieve_images_projects(user['username'])

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
            if file['user'] == username:
                images.append(file)

    return images


# Function for retrieving projects images
def retrieve_images_projects(username):
    return


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
        job_type = form.jobtype.data
        company_name = form.companyname.data
        description = form.description.data
        author = session['username']

        JobService.save(title, location, job_type, company_name, description, author)

        flash('Job posted', 'success')

        return redirect(url_for('jobs'))

    return render_template("post_job.html",form=form)

# Route for displaying all jobs
@app.route('/jobs')
def jobs():

    jobs = JobService.find_all()

    if len(jobs) > 0:
        return render_template('jobs.html', jobs=jobs)
    else:
        flash('No job found', 'danger')
        return render_template('jobs.html')


# ---!!! Jobs section fully implemented !!!---

# ---!!! Share folder for projects !!!---

@app.route('/projects')
def projects():

    projects = ProjectService.find_all_wip()

    if len(projects) > 0:
        return render_template('projects.html', projects=projects)
    else:
        flash('No project found', 'danger')
        return render_template('projects.html')


@app.route('/user_projects')
def user_projects():

    projects = ProjectService.find_all_by_username(session['username'])

    return render_template('projects.html', projects=projects)


@app.route('/add_project', methods=['POST', 'GET'])
def add_project():

    form = ProjectForm(request.form)

    if request.method == 'POST':

        title = form.title.data
        description = form.description.data
        max_number = form.max_number.data
        skills = form.skills.data
        author = session['username']
        appliers = []
        collaborators = []
        status = 'In search'
        files = []

        ProjectService.save(title, author, description, max_number, skills, status, collaborators, appliers, files)

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

    project = ProjectService.find_by_title(title)

    appliers = project.appliers

    if request.method == 'POST':

        ProjectService.put_in_collaborators(title, form.appliers.data)
        flash('Great! Your collaborators are ready', 'success')

        return redirect(url_for('single_project', title=project.title))

    else:

        files = project.files

        form.push_appliers(appliers)

        return render_template('single_project.html', project=project, form=form, files=files)


# Route for displaying single project when you click on the final image
@app.route('/image_project/<string:title>', methods=['POST', 'GET'])
def image_project(title):
    project = ProjectService.find_by_title(title)

    return render_template('image_project.html', project=project)


# Route for upload file in a specific project
@app.route('/projects/<string:title>/upload_file_project', methods=['POST', 'GET'])
def upload_file_project(title):

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('single_project', title=title))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('single_project', title=title))
        else:

            ProjectService.store_file_for_project(session['username'], title, file.filename, datetime.date.today(), request.form['description'], file)

            flash('File Uploaded', 'success')

            return redirect(url_for('single_project', title=title))

    return render_template('upload_file_project.html')


# Route for send files to user
@app.route('/projects/<string:title>/<string:file_name>')
def send_file_of_project(title, file_name):
    return ProjectService.send_image(title, file_name)


# Route for complete the project
@app.route('/projects/<string:title>/complete_project', methods=['POST', 'GET'])
def complete_project(title):
    project = ProjectService.find_by_title(title)

    if request.method == 'GET':
        files = []

        for file in project.files:
            list = file['file_name'].split('.')
            if len(list) > 1 and (list[1] == "jpg" or list[1] == "JPG" or list[1] == 'jpeg' or list[1] == 'png'):
                files.append(file)

        return render_template('complete_project.html', files=files, project=project)
    else:
        file_name = request.form['file_name']
        ProjectService.store_final_image(title, file_name)
        return redirect(url_for('image_project', title=title))


# Route for Complete works
@app.route('/complete_works')
def complete_works():

    # Checking how many complete projects there are in db
    projects = ProjectService.find_finished_project()

    if len(projects) > 0:
        # Fetching all complete projects
        return render_template('complete_works.html',projects=projects)
    else:
        flash('No project found', 'danger')
        return render_template('complete_works.html')


# Route for searching
@app.route('/search', methods=['POST','GET'])
def search():
    if request.method == 'POST':
        username = request.form['q']
        user = mongo.db.user.find_one({'username': username})
        if user is not None:
            return redirect(url_for('other_profile',username=username))
        else:
            flash('No user found', 'danger')
            return render_template('home.html')


# Check name of application
if __name__ == "__main__":
    app.run()
