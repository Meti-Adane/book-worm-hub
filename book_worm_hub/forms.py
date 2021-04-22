from db import checkField 
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, ValidationError
from wtforms.validators import Email, DataRequired, EqualTo, Length


class RegistrationForm(FlaskForm):
    # firstname = StringField('First name', validators=[DataRequired()])
    # lastname = StringField('lastname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=100)])
    confirmPassword = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')
    def validate_email(self, email):
        isEmailExist = checkField("users", "email", self.email.data)
        if isEmailExist:
            ValidationError("This email is already in use! Login to your account or try a new Email")
        
    
class LoginForm(FlaskForm):
    email = StringField('Email, Username', validators=[DataRequired()])    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=100)])
    submit = SubmitField('Sign in') 
    
