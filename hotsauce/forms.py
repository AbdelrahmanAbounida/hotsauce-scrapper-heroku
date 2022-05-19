from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField,EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from hotsauce.Models import User
from flask_login import current_user
class RegisterationForm(FlaskForm):

    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])

    email = EmailField('Email',
                        validators=[DataRequired(), Email("PLease enter a correct email address")])
    
    password = PasswordField('Password',
                        validators=[DataRequired()])
    
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(),EqualTo('password')])
    
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
    
        user = User.query.filter_by(email=email.data).first()
        if user:
            print(user)

            raise ValidationError("Opss!! a user with same email already exists.")

    def validate_username(self,username):
    
        user = User.query.filter_by(username=username.data).first()
        if user:
            print(user)
            raise ValidationError("Opss!! a user with same name already exists.")

class LoginForm(FlaskForm):
                           
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    password = PasswordField('Password',
                        validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Log in')


class UpdateAccountForm(FlaskForm):
    
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])

    email = EmailField('Email',
                        validators=[DataRequired(), Email("PLease enter a correct email address")])
    
    password = PasswordField('Password',
                        validators=[DataRequired()])
    
    
    submit = SubmitField('Update')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Send New Password')

    def validate_email(self,email):      
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            print("fault email")
            raise ValidationError("There is no Account with this email. Create new Account first!")


class ResetPasswordForm(FlaskForm):
                           
    password = PasswordField('Password',
                        validators=[DataRequired()])
    
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Submit')

    