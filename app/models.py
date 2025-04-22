# models.py

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, total_spent=0.0, favorite=None):
        self.username = username
        self.password = password
        self.total_spent = total_spent
        self.favorite = favorite

    def get_id(self):
        return self.username

    @property
    def id(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
