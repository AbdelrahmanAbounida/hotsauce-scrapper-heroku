

from operator import le
import re

from attr import has
from hotsauce.Models import User, Product
from flask import flash, redirect, render_template, url_for,jsonify,send_file
from hotsauce.forms import (LoginForm, RegisterationForm,
            UpdateAccountForm,RequestResetForm,ResetPasswordForm)
from hotsauce import app
import csv


# scraping
import crochet
import os
crochet.setup()
from crochet import wait_for, run_in_reactor

from flask import  render_template, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from s.Sauce.sauce.sauce.spiders.run import HotSauce

from flask_bcrypt import Bcrypt
from flask_login import login_user,current_user, logout_user, login_required
from hotsauce import db,mail

from flask_mail import Message
import smtplib
from email.message import EmailMessage

### global variables
global_close_flag = False
global_open_flag = False

output_data = []
data_length=-1
crawl_runner = CrawlerRunner()
global user_id 
bcrypt = Bcrypt(app)
spiderClosing = False



###########################################################################################################
                                 ############ scraping page ##############
###########################################################################################################
@app.route("/scrape")
@login_required
def scrape():
   user_id = current_user.id

   #current_user.spiderRunning = False 
   products = Product.query.filter_by(user_id=user_id).all()

   if len(products) > 0:
         if len(Product.query.filter_by(user_id=-2).all()) !=0:
            add_items_to_db()  
            #flash(f'Done! {len(output_data)} products have been scrapped.','success')
            current_user.spiderRunning = False
            db.session.commit()                 
            return render_template('scrape.html',downloadStatus = True,firstTime=False)
   else:
          if not current_user.spiderRunning:
             return render_template('scrape.html',downloadStatus = False,firstTime=True)
   
   
   return render_template('scrape.html',downloadStatus = False,firstTime=False)
             


###########################################################################################################
                                 ############ First scraping process ##############
###########################################################################################################
@app.route("/scrapePage")
@login_required
def startScraping():
   #current_user.firstTimeScraping = False
   #################### Scraping for the first time ########################
   if(not current_user.firstTimeScraping):  
      print("first Time")
      current_user.firstTimeScraping = True 
      current_user.spiderRunning = True 
      db.session.commit()
      scrape_with_crochet()
      return render_template('scrape.html',downloadStatus = False,firstTime=False)

   #################### when refresh the page and the scrapping process done ########################
   elif current_user.spiderRunning:
         if(len(output_data) != 0):
                  print("Spider is running and len of output is not zero")
                  if len(Product.query.filter_by(user_id=-2).all()) !=0:
                        print("Spider finished scrapping")
                        add_items_to_db()  
                        #flash(f'Done! {len(output_data)} products have been scrapped.','success')
                        current_user.spiderRunning = False
                        db.session.commit()
                        return render_template('scrape.html',downloadStatus = True,firstTime=False)
                  else:
                        print("Spider still scrapping")
                        return render_template('scrape.html',downloadStatus = False,firstTime=False)
         else:
            print("Spider is running and len of output is zero")
            return render_template('scrape.html',downloadStatus = False,firstTime=False)  
                        
   else:
   #################### when refresh the page and the scrapper still working ########################
      if len(Product.query.filter_by(user_id=current_user.id).all()) !=0:
            print("user has a database")
            return render_template('scrape.html',downloadStatus = True,firstTime=False)
      else:
            print("user doesn't have a database")
            return render_template('scrape.html',downloadStatus = False,firstTime=False)


def add_items_to_db():     
      print(f"curent user id: {current_user.id}") 
      for item in output_data:
         prod = Product(title=item['Title'],inStock=item['Status'],closeStatus=item['close'],user_id=current_user.id)
         p = Product.query.filter_by(title=item['Title']).first()
         if(p is None):
            db.session.add(prod)
            db.session.commit()
            print(prod)



from twisted.internet import reactor
@run_in_reactor
def scrape_with_crochet():
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(HotSauce)
    #eventual.addCallback(before) 
    #eventual.addBoth(lambda _: reactor.stop())
    reactor.run()
    reactor.stop()
    #eventual.addCallback(after) 
    return eventual


#This will append the data to the output data list.
def _crawler_result(item, response, spider):
       
   output_data.append(dict(item))
   


###########################################################################################################
                                 ############ Rescraping ##############
###########################################################################################################
@app.route("/rescrape")
@login_required
def rescrape():
   user_id = current_user.id
   prods = Product.query.filter_by(user_id=user_id).all()
   if(not current_user.spiderRunning):   # spider is not running
      current_user.spiderRunning = True 
      db.session.commit()

      try:
        
         for i in prods:              
            db.session.delete(i)
            db.session.commit()
         print("all products have been deleted")
      except:
         print("product can't be deleted from routes")
      scrape_with_crochet()  
      return render_template('scrape.html',downloadStatus = False,firstTime=False)
   else:
         if(len(output_data) != 0):
                  print("Spider is running and len of output is not zero")
                  if len(Product.query.filter_by(user_id=-2).all()) !=0:
                        
                        print("Spider finished scrapping")
                        add_items_to_db()  
                        flash(f'Done! {len(output_data)} products have been scrapped.','success')
                        current_user.spiderRunning = False
                        db.session.commit()
                        return render_template('scrape.html',downloadStatus = True,firstTime=False)
                  else:
                        print("Spider still scrapping")
                        return render_template('scrape.html',downloadStatus = False,firstTime=False)
         else:
            print("Spider is running and len of output is zero")
            return render_template('scrape.html',downloadStatus = False,firstTime=False)



###########################################################################################################
                                 ############ Home ##############
###########################################################################################################
@app.route("/home")
@app.route("/")
def home():
   if request.method == 'POST':
        if os.path.exists("sauces.db"): 
            os.remove("sauces.db")
            return redirect(url_for('scrape'))
   return render_template('home.html')


###########################################################################################################
                                 ############ Download CSV ##############
###########################################################################################################

@app.route("/download")
@login_required
def download(): 

   page = request.args.get('page')
   if page and page.isdigit():
      page = int(page)
   else:
      page = 1
   
   products = Product.query.filter_by(user_id=current_user.id)
   pages = products.paginate(page=page,per_page=10)
   prods_len = len(products.all())
   return render_template('download.html',products=products,pages=pages,prods_len=prods_len)


@app.route('/getCSV') 
def getCSV():
    return send_file('../sauces.csv',
                     mimetype='text/csv',
                     attachment_filename='sauces.csv',
                     as_attachment=True)

###########################################################################################################
                                 ############ Live Search ##############
###########################################################################################################

@app.route('/search',methods=['POST','GET'])
def search():
       
   if request.method == 'POST':
      search_word = request.get_data( as_text= True).split('q=')[-1] .replace('+',' ')
      result = db.engine.execute(f"SELECT id,title,inStock FROM Product WHERE title LIKE '%{search_word}%' AND user_id={current_user.id}  ORDER BY id  LIMIT 20 ")
      prods = [row for row in result]
      print(search_word)
      if len(prods):
             print(prods[0].title)
   else:
      search_word = ''
      prods =  Product.query.filter_by(user_id=-5) # just to return none

   return render_template('search.html',products=prods,srchtext = search_word)

###########################################################################################################
                                 ############ Search ##############
###########################################################################################################



###########################################################################################################
                                 ############ Register ##############
###########################################################################################################
@app.route("/register",methods=['GET','POST'])
def register():

   form = RegisterationForm()
   if form.validate_on_submit():
          ## getting user data
          hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
          user = User(username = form.username.data,email = form.email.data, password = hashedPassword)
          db.session.add(user)
          db.session.commit()
          flash(f'Account Created for {form.username.data}','success')
          return redirect(url_for('home'))

   return render_template('register.html', form=form)


###########################################################################################################
                                 ############ Login ##############
###########################################################################################################
@app.route("/login",methods=['GET','POST'])
def login():
   if current_user.is_authenticated:
          return redirect(url_for('home'))
   form = LoginForm()
   if form.validate_on_submit():
         user = User.query.filter_by(email=form.email.data).first()
         if user and bcrypt.check_password_hash(user.password,form.password.data):
                 login_user(user,remember=form.remember.data)
                 #flash('You have been login in!', 'success')
                 return redirect(url_for('home'))
         else:
                flash('Login unsuccessful. Please check your email or password', 'warning')

   return render_template('login.html', form=form)


###########################################################################################################
                                 ############ MyAccount ##############
###########################################################################################################

@app.route("/account",methods=['GET','POST'])
@login_required
def account():

   form = UpdateAccountForm() 
   if form.validate_on_submit():
          ## check if the password is correct
          if bcrypt.check_password_hash(current_user.password,form.password.data): 
               newUsername = form.username.data
               newEmail = form.email.data
               
               ## check if the email is not exist                     
               if User.query.filter_by(email=newEmail).first()  and newEmail != current_user.email:
                  flash('Opss!! a user with same email already exists.','danger') 

               ## check if the username is not exist
               elif User.query.filter_by(username=newUsername).first() and newUsername != current_user.username: 
                  flash('Opss!! a user with same name already exists.','danger') 
               elif newEmail != current_user.email or newUsername != current_user.username:                     
                  current_user.username = form.username.data
                  current_user.email = form.email.data
                  db.session.commit()
                  flash('Your account has been updated', 'success')         
          else:                
               flash('The password is incorrect', 'danger')   

   elif request.method == 'GET':
          form.username.data = current_user.username
          form.email.data = current_user.email
   
   return render_template('account.html',form=form)
   

###########################################################################################################
                                 ############ confirm email before reset ##############
###########################################################################################################

def sendFlaskEmail(user,token):
      msg = Message("Reset HotSauce Scrapper Password"
               ,sender=app.config['MAIL_USERNAME']
               ,recipients=[user.email])

      msg.body = f'''
               To reset Your Password, Please visit the following link:
               {url_for('reset_password',token=token,_external=True)}
            '''
      mail.send(msg)
      print("Message Has been sent!!")

##############################################
def create_msg(subject,body,FROM,TO):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg.set_content(body)
    msg['From'] = FROM
    msg['To'] = TO # get a list 

    return msg


def sendEmail(user,token):
   FROM = app.config['MAIL_USERNAME']
   TO = [user.email] # must be a list
   print(user.email)
   subject = "Reset HotSauce Scrapper Password"
   with smtplib.SMTP('smtp.gmail.com',587) as server:
        server.ehlo() # Identify myself
        server.starttls() #Put the SMTP connection in TLS (Transport Layer Security) mode
        server.ehlo() # should be called again, acc.to documentation
        server.login(app.config['MAIL_USERNAME'],app.config['MAIL_PASSWORD'])

        body = f'''
               To reset Your Password, Please visit the following link:
               {url_for('reset_password',token=token,_external=True)}
            '''
        msg = create_msg(subject,body,FROM,TO)
        server.send_message(msg)
        server.quit()


def send_restPass_email(user):
   
   token = user.get_reset_token()
   sendEmail(user,token)
   print("Email has been sent")
   #sendFlaskEmail(user,token)
   
@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
   if current_user.is_authenticated:
          return redirect(url_for('home'))

   form = RequestResetForm() 

   if form.validate_on_submit():
         email = form.email.data
         user = User.query.filter_by(email=email).first()
         send_restPass_email(user)
         flash('An email has been send with instructions to reset your password','success')
         return redirect(url_for('reset_request'))

      
   return render_template('confirm_email.html',form=form)


###########################################################################################################
                                 ############ Reset Password ##############
###########################################################################################################

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
   if current_user.is_authenticated:
          return redirect(url_for('home'))

   user = User.verify_reset_token(token)

   if user is None:
      flash('This is an invalid or expired token ','warning')
      return redirect(url_for('reset_request'))
    
   form = ResetPasswordForm() 
   if form.validate_on_submit():
         password = form.password.data
         confirm_password = form.confirm_password.data
         if password != confirm_password:
                flash('Please check that password confirmation is correct','warning')
                return render_template('confirm_email.html',form=form)
         hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')
         user.password = hashedPassword
         db.session.commit()
         flash('Your password has been updated!','success')
         return redirect(url_for('login'))

   return render_template('reset_password.html',form=form)


###########################################################################################################
                                 ############ Errors ##############
###########################################################################################################

@app.errorhandler(404)
def error_404(error):
    return render_template('errors/error404.html'), 404

@app.errorhandler(403)
def error_403(error):
    return render_template('error403.html'), 403

   
@app.errorhandler(500)
def error_500(error):
    return render_template('error500.html'), 500


###########################################################################################################
                                 ############ Logout ##############
###########################################################################################################
@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect('/login')

