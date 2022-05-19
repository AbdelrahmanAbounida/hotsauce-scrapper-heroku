from hotsauce import db
from flask_login import UserMixin
from hotsauce import login_manager,app
from itsdangerous import URLSafeTimedSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
############ DataBase ##############
class User(db.Model, UserMixin):
       
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    email = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(50) ,nullable=False)
    products = db.relationship('Product',backref='author',lazy=True)
    spiderRunning = db.Column(db.Boolean, default=False)
    firstTimeScraping = db.Column(db.Boolean, default=False)

    def get_reset_token(self): # user will be logged out after 3000 seconds
        s = Serializer(app.config['SECRET_KEY'])
        print(s.dumps({'user_id':self.id}))
        return s.dumps({'user_id':self.id})
    
    @staticmethod
    def verify_reset_token(token,max_age=3000):
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token,max_age=max_age)['user_id']
        except:
            return None

        return User.query.get(user_id)
        
    def __repr__(self):
           return f"user: ({self.username},{self.email})"

class Product(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.Text)
   inStock = db.Column(db.Text)
   openStatus = db.Column(db.Boolean)
   closeStatus = db.Column(db.Boolean)
   item_scrapped_count = db.Column(db.Integer)
   user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

   def __repr__(self):
           return f"({self.title},{self.inStock})"
