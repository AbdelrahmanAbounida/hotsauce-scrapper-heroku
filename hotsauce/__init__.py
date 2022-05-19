from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
app = Flask(__name__)

app.config['SECRET_KEY'] = '598849722efc0faeb634444805fec10e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sauces.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['USE_TLS'] = True
app.config['USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hotsaucescrapper581@gmail.com'
app.config['MAIL_PASSWORD'] = 'Aa2964079'

mail = Mail()
mail.init_app(app)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_message = "You have to login to start scrapping"
login_manager.login_message_category = "danger"
login_manager.login_view = 'login' # name of the function that will be redirected incase of unauthenticated user 
from hotsauce import routes


    