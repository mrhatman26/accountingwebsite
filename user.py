from flask_login import UserMixin
class User(UserMixin):
    def __init__(self, id, username, is_mod, is_admin):
        self.id = id
        self.username = username
        self.is_mod = is_mod
        self.is_admin = is_admin