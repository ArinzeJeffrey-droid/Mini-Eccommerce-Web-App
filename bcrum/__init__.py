from datetime import datetime
from flask import Flask, render_template, url_for,flash, redirect,request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'f67277f7e25ff7f796ae27118cf24a30'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bcrum.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'
login_manager.login_message_category = 'info'



from bcrum import routes