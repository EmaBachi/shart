from passlib.hash import sha256_crypt
import datetime
import os

from Repositories import UserRepository, ArticleRepository
from Domain import User, Article, Comment


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