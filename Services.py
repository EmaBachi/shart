from flask import send_from_directory
from passlib.hash import sha256_crypt
import os

from Repositories import UserRepository, ArticleRepository, ContestRepository, ExclusiveVideoRepository, JobRepository
from Domain import User, Article, Comment, Contest, File, ExclusiveVideo, Job

UPLOAD_FOLDER_CONTEST = '/home/emanuele/Scrivania/Shart_Contents/contests'


def create_directory_for_contest(title):
    directory = UPLOAD_FOLDER_CONTEST + "/" + title
    if not os.path.exists(directory):
        os.makedirs(directory)
    return


def save_image_in_server(title, image_to_save, file_to_save):
    path = os.path.join(UPLOAD_FOLDER_CONTEST + "/" + title, image_to_save)
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
        save_image_in_server(title, image_to_save, file_to_save)

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