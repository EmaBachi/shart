from flask import send_from_directory
from passlib.hash import sha256_crypt
import os

from Repositories import UserRepository, ArticleRepository, ContestRepository, ExclusiveVideoRepository, JobRepository, ProjectRepository
from Domain import User, Article, Comment, Contest, File, ExclusiveVideo, Job, Project

UPLOAD_FOLDER_CONTEST = '/home/emanuele/Scrivania/Shart_Contents/contests'
UPLOAD_FOLDER_PROJECT = '/home/emanuele/Scrivania/Shart_Contents/projects'
UPLOAD_FOLDER_IMAGE = '/home/emanuele/Scrivania/Shart_Contents/images'


def create_directory_for_contest(title):
    directory = UPLOAD_FOLDER_CONTEST + "/" + title
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


def save_image_contest_in_server(title, image_to_save, file_to_save):
    path = os.path.join(UPLOAD_FOLDER_CONTEST + "/" + title, image_to_save)
    file_to_save.save(path)


def create_directory_for_project(title_project):
    directory = UPLOAD_FOLDER_PROJECT + "/" + title_project
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


def save_image_project_in_server(title, file_to_save):
    path = os.path.join(UPLOAD_FOLDER_PROJECT + "/" + title, file_to_save.filename)
    file_to_save.save(path)
    return


def store_profile_image(file_to_save):
    path = os.path.join(UPLOAD_FOLDER_IMAGE, file_to_save.filename)
    file_to_save.save(path)


class UserService:

    # Method that tries to create a user
    @staticmethod
    def create_user(first_name, surname, username, date_of_birth, country, email, password_no_crypt,
                    type):

        if UserRepository.already_username(username) == 0:

            password = sha256_crypt.encrypt(str(password_no_crypt))

            user = User(first_name, surname, username, date_of_birth, country, email, password,
                        type, False, "", "", "")

            UserRepository.create_user(user)

            return True

        else:
            return False

    @staticmethod
    def find_user_by_username(username):

        user_dict = UserRepository.find_by_username(username)

        try:
            len(user_dict)

            user = User(user_dict['first_name'], user_dict['surname'], user_dict['username'],
                        user_dict['date_of_birth'], user_dict['country'], user_dict['email'],
                        user_dict['password'], user_dict['type'], user_dict['adm'], user_dict['path'],
                        user_dict['image_name'], user_dict['description'])

            return user

        except TypeError:

            return None

    # Method that login one user
    @staticmethod
    def login(username_candidate, password_candidate):

        user_dict = UserRepository.find_by_username(username_candidate)

        try:
            len(user_dict)

            password_user = user_dict['password']

            # Check the password
            if sha256_crypt.verify(password_candidate, password_user):

                user = User(user_dict['first_name'], user_dict['surname'], user_dict['username'],
                            user_dict['date_of_birth'], user_dict['country'], user_dict['email'],
                            user_dict['password'], user_dict['type'], user_dict['adm'], user_dict['path'],
                            user_dict['image_name'], user_dict['description'])

                return user

            else:
                return None

        except TypeError:

            return None

    # Method to set profile image
    @staticmethod
    def set_profile_image(username, file_to_save):
        UserRepository.set_profile_image(username, UPLOAD_FOLDER_IMAGE, file_to_save.filename)
        store_profile_image(file_to_save)

    # Method to send profile image
    @staticmethod
    def send_file(image_name):
        return send_from_directory(UPLOAD_FOLDER_IMAGE, image_name)

    # Method to change description
    @staticmethod
    def change_description(username, description):
        UserRepository.change_description(username, description)

    # Method to change password
    @staticmethod
    def change_password(old_password, new_password, username):
        user_dict = UserRepository.find_by_username(username)

        user = User(user_dict['first_name'], user_dict['surname'], user_dict['username'],
                    user_dict['date_of_birth'], user_dict['country'], user_dict['email'],
                    user_dict['password'], user_dict['type'], user_dict['adm'], user_dict['path'],
                    user_dict['image_name'], user_dict['description'])

        if sha256_crypt.verify(old_password, user.password):
            password = sha256_crypt.encrypt(str(new_password))
            UserRepository.change_password(user.username, password)
            return True
        else:
            return False


class ArticleService:

    # Method to find all articles
    @staticmethod
    def find_all_articles():
        articles_dict = ArticleRepository.find_all_articles()
        articles = []

        for article in articles_dict:
            temp = Article(article['author'], article['title'], article['body'], article['date'], article['comments'])
            articles.append(temp)

        return articles

    # Method to find article by title
    @staticmethod
    def find_by_title(title):
        article = ArticleRepository.find_by_title(title)
        temp = Article(article['author'], article['title'], article['body'], article['date'], article['comments'])
        return temp

    # Method to add one comment to one article
    @staticmethod
    def add_comment_to_article(article, comment_author, comment_body, comment_date):
        comment = Comment(comment_author, comment_body, str(comment_date))
        ArticleRepository.add_comment_to_article(article.title, comment)
        return

    # Method to ave one article
    @staticmethod
    def save(title, body, author, date):
        article = Article(author, title, body, str(date), [])
        ArticleRepository.save(article)

    # Method to edit an add_comment_to_article
    @staticmethod
    def edit(title, body, author, date):
        temp = ArticleRepository.find_by_title(title)
        article = Article(author, title, body, str(date), temp['comments'])
        ArticleRepository.edit(article)

    # Method to remove an article
    @staticmethod
    def remove(article_title):
        ArticleRepository.remove(article_title)


class ContestService:

    # Method to find all contests
    @staticmethod
    def find_all_contests():
        contests_dict = ContestRepository.find_all_contests()
        contests = []

        for contest in contests_dict:
            temp = Contest(contest['title'], contest['author'], contest['body'],
                           contest['presentation_deadline'], contest['enroll_deadline'],
                           contest['type'], contest['folder'], contest['comments'], contest['competitors'],
                           contest['files'])
            contests.append(temp)

        return contests

    # Method to find one contest by its title
    @staticmethod
    def find_by_title(title):
        contest = ContestRepository.find_by_title(title)
        temp = Contest(contest['title'], contest['author'], contest['body'],
                       contest['presentation_deadline'], contest['enroll_deadline'],
                       contest['type'], contest['folder'], contest['comments'], contest['competitors'],
                       contest['files'])
        return temp

    # Method to add one comment to a contest
    @staticmethod
    def add_comment_to_contest(contest, comment_author, comment_body, comment_date):
        comment = Comment(comment_author, comment_body, str(comment_date))
        ContestRepository.add_comment_to_contest(contest.title, comment)

    # Method to add a contest
    @staticmethod
    def save(title, author, body, type, presentation_deadline, enroll_deadline):
        contest = Contest(title, author, body, presentation_deadline, enroll_deadline,
                       type, title, [], [], [])
        ContestRepository.save(contest)
        create_directory_for_contest(title)

    # Method to edit a contest
    @staticmethod
    def edit(title, body, author):
        temp = ContestRepository.find_by_title(title)
        contest = Contest(title, author, body, temp['presentation_deadline'], temp['enroll_deadline'],
                          temp['type'], temp['folder'], temp['comments'], temp['competitors'],
                          temp['files'])
        ContestRepository.edit(contest)

    # Method to remove a contest
    @staticmethod
    def remove(title):
        ContestRepository.remove(title)

    # Method to join a contest
    @staticmethod
    def join_contest(title, username):
        ContestRepository.join_contest(title, username)

    # Method to upload a project in a contest
    @staticmethod
    def upload_project_contest(username, title, image_to_save, file_to_save):
        file = File(username, image_to_save, UPLOAD_FOLDER_CONTEST, title, "", 0, 0, "")
        ContestRepository.upload_project_contest(title, file)
        save_image_contest_in_server(title, image_to_save, file_to_save)

    # Method to display the image
    @staticmethod
    def send_image(title, file_name):
        return send_from_directory(UPLOAD_FOLDER_CONTEST+"/"+title, file_name)

    # Method to find contest by username
    @staticmethod
    def find_contest_by_user(username):
        contests_dict = ContestRepository.find_contest_by_user(username)
        contests = []

        for contest in contests_dict:
            temp = Contest(contest['title'], contest['author'], contest['body'],
                           contest['presentation_deadline'], contest['enroll_deadline'],
                           contest['type'], contest['folder'], contest['comments'], contest['competitors'],
                           contest['files'])
            contests.append(temp)

        return contests

    # Method to like a project
    @staticmethod
    def like(title, name):
        ContestRepository.like(title, name)

    # Method to like a project
    @staticmethod
    def unlike(title, name):
        ContestRepository.unlike(title, name)

    # Method to retrieve user's images contest
    @staticmethod
    def retrieve_images_contest(username):

        query = ContestRepository.retrieve_images_contest(username)

        images = []

        for item in query:
            for file in item['files']:
                if file['user'] == username:
                    images.append(file)

        return images


class ExclusiveVideoService:

    # Method to save a video
    @staticmethod
    def save(description, video_name, url_video):
        exclusive_video = ExclusiveVideo(url_video, description, video_name)
        ExclusiveVideoRepository.save(exclusive_video)

    # Method to find all exclusive videos
    @staticmethod
    def find_all():
        video_dict = ExclusiveVideoRepository.find_all()
        videos = []

        for video in video_dict:
            temp = ExclusiveVideo(video['url_video'], video['description'], video['video_name'])
            videos.append(temp)

        return videos

    # Method to remove a video
    @staticmethod
    def remove(video_name):
        ExclusiveVideoRepository.remove(video_name)


class JobService:

    # Method to save a job
    @staticmethod
    def save(title, location, author, job_type, description, company_name):
        job = Job(author, title, description, company_name, location, job_type)
        JobRepository.save(job)

    # Method to find all jobs
    @staticmethod
    def find_all():
        job_dict = JobRepository.find_all()
        jobs = []

        for job in job_dict:
            temp = Job(job['author'], job['title'], job['description'], job['company_name'],
                       job['location'], job['job_type'])
            jobs.append(temp)

        return jobs


class ProjectService:

    # Method to find all project with status wip or in search
    @staticmethod
    def find_all_wip():
        project_dict = ProjectRepository.find_all_wip()

        projects = []

        for temp in project_dict:
            project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                              temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                              temp['files'], temp['final_image'])
            projects.append(project)

        return projects

    # Method to find all project related to an user
    @staticmethod
    def find_all_by_username(username):
        project_dict = ProjectRepository.find_all_by_username(username)

        projects = []

        for temp in project_dict:
            project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                              temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                              temp['files'], temp['final_image'])
            projects.append(project)

        return projects

    # Method to find all project related to an user giving a certain status
    @staticmethod
    def find_all_by_username_and_status(username, status):
        project_dict = ProjectRepository.find_all_by_username_and_status(username, status)

        projects = []

        for temp in project_dict:
            project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                              temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                              temp['files'], temp['final_image'])
            projects.append(project)

        return projects

    # Method to save a project
    @staticmethod
    def save(title, author, description, max_number, skills, status, collaborators, appliers, files):
        project = Project(author, title, description, max_number, skills, status, appliers, collaborators,
                          files, "")
        ProjectRepository.save(project)

    # Method to join a project
    @staticmethod
    def join_project(title, username):
        ProjectRepository.join_project(title, username)

    # Method to find a project by its title
    @staticmethod
    def find_by_title(title):
        temp = ProjectRepository.find_by_title(title)

        project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                          temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                          temp['files'], temp['final_image'])

        return project

    # Method to check how many collaborators there are in a given projects
    @staticmethod
    def check_collaborators_number(title)
    

    # Method to put some users into collaborators
    @staticmethod
    def put_in_collaborators(title, collaborators):
        ProjectRepository.put_in_collaborators(title, collaborators)

        temp = ProjectRepository.find_by_title(title)

        project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                          temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                          temp['files'], temp['final_image'])

        if project.max_number == len(project.collaborators):
            create_directory_for_project(project.title)
            ProjectRepository.change_status(project.title, 'WIP')

    # Method to store a file in a project
    @staticmethod
    def store_file_for_project(username, title, file_name, date, description, file_to_save):
        file = File(username, file_name, UPLOAD_FOLDER_PROJECT, title, description, 0, 0, str(date))
        ProjectRepository.store_file_for_project(title, file)
        save_image_project_in_server(title, file_to_save)

    # Method to send an image from directory
    @staticmethod
    def send_image(title, file_name):
        return send_from_directory(UPLOAD_FOLDER_PROJECT + "/" + title, file_name)

    # Method to store the final image of a project
    @staticmethod
    def store_final_image(title, final_image):
        ProjectRepository.store_final_image(title, final_image)
        ProjectRepository.change_status(title, 'finished')

    # Method to find finished project
    @staticmethod
    def find_finished_project():
        project_dict = ProjectRepository.find_finished_project()

        projects = []

        for temp in project_dict:
            project = Project(temp['author'], temp['title'], temp['description'], temp['max_number'],
                              temp['skills'], temp['status'], temp['appliers'], temp['collaborators'],
                              temp['files'], temp['final_image'])
            projects.append(project)

        return projects
