# Entities file


class User:

    def __init__(self, first_name, surname, username, date_of_birth, country, email, password,
                 type, adm, path, image_name, description):
        self.first_name = first_name
        self.surname = surname
        self.username = username
        self.date_of_birth = date_of_birth
        self.country = country
        self.email = email
        self.password = password
        self.type = type
        self.adm = adm
        self.path = path
        self.image_name = image_name
        self.description = description


class Article:

    def __init__(self, author, title, body, date, comments):
        self.author = author
        self.title = title
        self.body = body
        self.date = date
        self.comments = comments


class Comment:

    def __init__(self, author, body, date):
        self.author = author
        self.body = body
        self.date = date


class Job:

    def __init__(self, author, title, description, company_name, location, job_type):
        self.author = author
        self.title = title
        self.description = description
        self.company_name = company_name
        self.location = location
        self.job_type = job_type


class ExclusiveVideo:

    def __init__(self, url_video, description, video_name):
        self.url_video = url_video
        self.description = description
        self.video_name = video_name


class Contest:

    def __init__(self, title, author, body, presentation_deadline, enroll_deadline, type, folder,
                 comments, competitors, files_project):
        self.title = title
        self.author = author
        self.body = body
        self.presentation_deadline = presentation_deadline
        self.enroll_deadline = enroll_deadline
        self.type = type
        self.folder = folder
        self.comments = comments
        self.competitors = competitors
        self.files_project = files_project


class File:

    def __init__(self, user, file_name, primary_folder, secondary_folder, description, like, unlike, date):
        self.user = user
        self.file_name = file_name
        self.primary_folder = primary_folder
        self.secondary_folder = secondary_folder
        self.description = description
        self.like = like
        self.unlike = unlike
        self.date = date


class Project:

    def __init__(self, author, title, description, max_number, skills, status, appliers,
                 collaborators, files, final_image):
        self.author = author
        self.title = title
        self.description = description
        self.max_number = max_number
        self.skills = skills
        self.status = status
        self.appliers = appliers
        self.collaborators = collaborators
        self.files = files
        self.final_image = final_image


