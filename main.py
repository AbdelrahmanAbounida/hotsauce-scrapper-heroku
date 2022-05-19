from hotsauce.Models import Product, User
from hotsauce import app,db
from os.path import exists
if __name__ == '__main__':
       
   if not exists('sauces.db'):
      db.create_all()
   else:
      print("sauces.db already exists")

   app.debug = True
   app.run()

