import os
from flask import Flask
from flask_login import LoginManager
from flask_argon2 import Argon2

#Init the extensions
login_manager = LoginManager()
argon2 = Argon2()

def create_app(template_folder=None, static_folder=None):
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    #Use a secure random secret key
    app.secret_key = os.urandom(24)

    from app.utils import load_users
    from app.models import User

    #Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    #Initialize Argon2 for password hashing
    argon2.init_app(app)

    #Define the user_loader callback for flask-login
    @login_manager.user_loader
    def load_user(user_id):
        users = load_users()
        user = users.get(user_id)
        #IF user is found, return the user_id, password, total_spent, and favorite
        if user:
            return User(user_id, user["password"], user.get("total_spent", 0.0), user.get("favorite"))
        return None

    #Register blueprint for views
    from app.views import bp as views_bp
    app.register_blueprint(views_bp)

    return app
