from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, role):
        self.id = str(id)  # Ensure the ID is a string for Flask-Login
        self.email = email
        self.password = password
        self.role = role
