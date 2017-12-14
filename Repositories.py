from pymongo import MongoClient

client = MongoClient(maxPoolSize=5)
db = client.shart


class UserRepository:

    # Method that checks whether a certain username has already been picked
    @staticmethod
    def already_username(username):
        count = db.user.find({'username': username}).count()
        return count

    # Method that creates one user
    @staticmethod
    def create_user(user):
        db.user.insert(
            {
                'first_name': user.first_name,
                'surname': user.surname,
                'username': user.username,
                'type': user.type,
                'date_of_birth': user.date_of_birth,
                'country': user.country,
                'email': user.email,
                'password': user.password,
                'adm': user.adm,
                'path': user.path,
                'image_name': user.image_name,
                'description': user.description
            }
        )

    # Method that looks for a user in db
    @staticmethod
    def find_by_username(username_candidate):
        user_dict = db.user.find_one({'username': username_candidate})
        return user_dict


class ArticleRepository:

    # Method to find al articles
    @staticmethod
    def find_all_articles():
        return db.article.find()

    # Method to find an article from its title
    @staticmethod
    def find_by_title(title):
        return db.article.find_one({'title': title})

    # Method to add one comment to one article
    @staticmethod
    def add_comment_to_article(title, comment):
        db.article.update(
            {'title': title},
            {'$push':
                 {"comments": {"author": comment.author,
                                'body': comment.body,
                               'date': comment.date
                               }
                  }
             }
        )

    # Method to save one article
    @staticmethod
    def save(article):
        db.article.insert(
            {
                'title': article.title,
                'author': article.author,
                'body': article.body,
                'date': article.date,
                'comments': article.comments
            }
        )

    # Method to edit an article
    @staticmethod
    def edit(article):
        db.article.update(
            {"title": article.title},
            {'$set': {"body": article.body,
                        "author": article.author,
                        "date": article.date,
                      'comments': article.comments
                      }
             }
        )

    # Method to remove an article
    @staticmethod
    def remove(article_title):
        db.article.remove({"title": article_title})


