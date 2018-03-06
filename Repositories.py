from pymongo import MongoClient


client = MongoClient("mongodb://emaBachi:1LGr3co1994?@shart-shard-00-00-q1do7.mongodb.net:27017,shart-shard-00-01-q1do7.mongodb.net:27017,shart-shard-00-02-q1do7.mongodb.net:27017/test?ssl=true&replicaSet=shart-shard-0&authSource=admin")
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
                'description': user.description,
                'gallery': user.gallery
            }
        )

    # Method that looks for a user in db
    @staticmethod
    def find_by_username(username_candidate):
        user_dict = db.user.find_one({'username': username_candidate})
        return user_dict

    # Method to set profile image
    @staticmethod
    def set_profile_image(username, path, file_name):
        db.user.update(
            {"username": username},
            {'$set':
                {
                    'path': path,
                    'image_name': file_name
                }
            }
        )

    # Method to change description
    @staticmethod
    def change_description(username, description):
        db.user.update(
            {'username': username},
            {'$set': {
                        'description': description
            }
            }
        )

    # Method to change password
    @staticmethod
    def change_password(username, password):
        db.user.update({"username": username},
                           {'$set':
                               {
                                   'password': password
                               }
                           }
                       )

    # Method to save a gallery to a gallery owner
    @staticmethod
    def save_gallery_to_user(username, gallery):
        db.user.update({
            "username": username
        },
            {
              "$set": {
                  "gallery": {
                      "gallery": gallery.gallery_name,
                      "city": gallery.city,
                      "address": gallery.address,
                      "lat": gallery.lat,
                      "long": gallery.long,
                      "website": gallery.website
                  }
              }
            })


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


class ContestRepository:

    # Method to find all contests
    @staticmethod
    def find_all_contests():
        return db.contest.find()

    # Method to find one contest by its title
    @staticmethod
    def find_by_title(title):
        return db.contest.find_one({'title': title})

    # Method to add comment to a contest
    @staticmethod
    def add_comment_to_contest(title, comment):
        db.contest.update(
            {
                'title': title
            },
            {'$push':
                 {"comments":
                      {"author": comment.author,
                        "body": comment.body,
                        "date": comment.date
                       }
                  }
             }
        )

    # Method to add a contest
    @staticmethod
    def save(contest):
        db.contest.insert(
            {
                'title': contest.title,
                'body': contest.body,
                'author': contest.author,
                'enroll_deadline': contest.enroll_deadline,
                'presentation_deadline': contest.presentation_deadline,
                'type': contest.type,
                'folder': contest.title,
                'files': [],
                'competitors': [],
                'comments': [],
                'winner': ""
            }
        )

    # Method to edit a contest
    @staticmethod
    def edit(contest):
        db.contest.update(
            {"title": contest.title},
            {'$set':
                {"body": contest.body,
                "author": contest.author,
                 }
             }
        )

    # Method to remove a contest
    @staticmethod
    def remove(title):
        db.contest.remove({'title': title})

    # Method to join a contest
    @staticmethod
    def join_contest(title, username):
        db.contest.update(
            {"title": title},
            {'$push':
                 {'competitors': username}
             }
        )

    # Method to upload a project in a contest
    @staticmethod
    def upload_project_contest(title, file):
        db.contest.update({'title': title},
                          {'$push':
                               {'files':
                                    {'user': file.user,
                                     'primary_folder': file.primary_folder,
                                     'secondary_folder': file.secondary_folder,
                                     'file_name': file.file_name,
                                     'like': file.like,
                                     'usernames_like': file.usernames_like,
                                     'usernames_unlike': file.usernames_unlike,
                                     'unlike': file.unlike
                                     }
                                }
                           })

    # Method to find contest by user
    @staticmethod
    def find_contest_by_user(username):
        return db.contest.find({'competitors': username})

    # Method to like a project
    @staticmethod
    def like(title, name,username):
        db.contest.update(
            {
                'title': title,
                'files.file_name': name},

            {'$inc':
                 {'files.$.like': 1}},

        )
        db.contest.update(
            {
                'title': title,
                'files.file_name': name},

            {'$push':
                 {'files.$.usernames_like': username}}
        )


    # Method to find all people who liked the project, given a file_name and contest's title
    @staticmethod
    def find_usernames_like(title, name):

        return db.contest.find(
            {
                'title': title,
                'files.file_name':name
            },
            {
                '_id': 0,

                'files.usernames_like': 1
            }
        )

    # Method to find all people who unliked the project, given a file_name and contest's title
    @staticmethod
    def find_usernames_unlike(title, name):
            return db.contest.find(
                {
                    'title': title,
                    'files.file_name': name
                },
                {
                    '_id': 0,

                    'files.usernames_unlike': 1
                }
            )

    # Method to like a project
    @staticmethod
    def unlike(title, name,username):
        db.contest.update(
            {
                'title': title,
                'files.file_name': name},
            {'$inc':
                {'files.$.unlike': 1}
            }
        )
        db.contest.update(
            {
                'title': title,
                'files.file_name': name},

            {'$push':
                 {'files.$.usernames_unlike': username}}
        )

    # Method to retrieve all contest's images of a user
    @staticmethod
    def retrieve_images_contest(username):
        return db.contest.find({
                            'files.user': username
                                },
                            {
                                '_id': 0,
                                'files': 1
                            }
        )

    #Method to find the winner of the project
    @staticmethod
    def set_winner(title, winner):
        db.contest.update(
            {"title": title},
            {"$set": {
                "winner": winner
            }}
        )


class ExclusiveVideoRepository:

    # Method to save a video
    @staticmethod
    def save(exclusive_video):
        db.exclusive_videos.insert({
            'description': exclusive_video.description,
            'video_name': exclusive_video.video_name,
            'url_video': exclusive_video.url_video
        })

    # Method to find all videos
    @staticmethod
    def find_all():
        return db.exclusive_videos.find()

    # Method to remove a video
    @staticmethod
    def remove(video_name):
        db.exclusive_videos.remove({"video_name": video_name})


class JobRepository:

    # Method to save a job
    @staticmethod
    def save(job):
        db.job.insert({
            'author': job.author,
            'title': job.title,
            'description': job.description,
            'company_name': job.company_name,
            'location': job.location,
            'job_type': job.job_type

        })

    # Method to find all jobs
    @staticmethod
    def find_all():
        return db.job.find()


class ProjectRepository:

    @staticmethod
    def find_all_wip():
        return db.project.find(
            {'$or':
                 [
                     {'status': 'WIP'},
                     {'status': 'In search'}
                 ]
            }
        )

    @staticmethod
    def find_all_by_username(username):
        return db.project.find({'$or': [{'author': username}, {'collaborators': {'$in': [username]}}]})

    @staticmethod
    def find_all_by_username_and_status(username, status):
        return db.project.find({'$or': [{'author': username, 'status': status}, {'collaborators': {'$in': [username]}, 'status': status}]})

    @staticmethod
    def save(project):
        db.project.insert({
            'title': project.title,
            'description': project.description,
            'author': project.author,
            'max_number': project.max_number,
            'skills': project.skills,
            'appliers': project.appliers,
            'collaborators': project.collaborators,
            'status': project.status,
            'files': project.files,
            'final_image': project.final_image
        })

    @staticmethod
    def join_project(title, username):
        db.project.update(
            {'title': title},
            {'$push':
                 {'appliers': username}
             }
        )

    @staticmethod
    def find_by_title(title):
        return db.project.find_one({'title': title})

    # Method to put some users into collaborators
    @staticmethod
    def put_in_collaborators(title, collaborators):
        db.project.update({'title': title}, {'$push': {'collaborators': {'$each': collaborators}}})
        db.project.update({'title': title}, {'$pullAll': {'appliers': collaborators}})

    # Method to change project status
    @staticmethod
    def change_status(title, status):
        db.project.update({'title': title}, {'$set': {'status': status}})

    # Method to store a file into a project
    @staticmethod
    def store_file_for_project(title, file):
        db.project.update(
            {
                'title': title
            },
            {
                '$push': {
                    'files': {
                        'primary_folder': file.primary_folder,
                        'secondary_folder': file.secondary_folder,
                        'file_name': file.file_name,
                        'user': file.user,
                        'date': file.date,
                        'description': file.description
                    }
                }
            }
        )

    # Method to store the final image of a project
    @staticmethod
    def store_final_image(title, final_image):
        db.project.update({
            'title': title
        },
            {
                "$set": {
                    'final_image': final_image
                }
            })

    # Method to find finished project
    @staticmethod
    def find_finished_project():
        return db.project.find({'status': 'finished'})

    # Method to find project files
    @staticmethod
    def find_project_files(title):
           return db.project.find({'title': title},
                                  {'_id':0,
                                   'files':1})
