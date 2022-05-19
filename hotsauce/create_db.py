
from hotsauce import db
from Models import Product, User
from os.path import exists


if not exists('sauces.db'):
       db.create_all()
else:
    print("sauces.db already exists")


## create some users
# user1 = User(username="Abonuida", email="aboneda@gmail.com",password="1234")
# db.session.add(user1)
# db.session.commit()

# user2 = User(username="Ali", email="ali@gmail.com",password="1234")
# db.session.add(user2)
# db.session.commit()

## add product
# user1 = User.query.first()
# user2 = User.query.get(2)

# prod1 = Product(title='Sauce1',inStock=True,user_id=user1.id)
# prod2 = Product(title='Sauce2',inStock=True,user_id=user2.id)

# db.session.add(prod1)
# db.session.add(prod2)

# db.session.commit()
## get all users
# print(User.query.all())
# print(User.query.first())
# print(User.query.filter_by(username='Abonuida').first())


## clear database
# db.drop_all()
# db.create_all()