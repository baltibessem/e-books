from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .models import User
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["SECRET_KEY"] = "6c591946e6c18ed81bb87b365aeec49440349882"
app.config["MONGO_URI"] = "mongodb+srv://xyz:123@cluster0.briuh.mongodb.net/mydb?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"

mongodb_client = PyMongo(app)
db = mongodb_client.db

# MongoDB, bcrypt et login manager
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.utilisateurs.find_one({'_id': ObjectId(user_id)})  # Ensure ObjectId is used
    if user_data:
        return User(user_data['_id'], user_data['email'], user_data['password'], user_data['role'])
    return None


from application import routes
