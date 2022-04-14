# from crypt import methods
from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager , login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms import StringField, PasswordField, SubmitField,validators
from wtforms.validators import InputRequired, length, ValidationError
from flask_bcrypt import Bcrypt
# Echoing password and masked with hashtag(#)
# import maskpass  # importing maskpass library
 
# prompt msg = Password and
# masking password with hashtag(#)
# pwd = maskpass.askpass(prompt="Password:", mask="*")
# print(pwd)

app = Flask(__name__)
db = SQLAlchemy(app)  #creates db instance
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db' #links db instance to app.py file
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager =LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


#return/callback user from LAST/CURRENT session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#table creation for sqlite
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True )
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)



#Register Form
class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), length( 
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = StringField(validators=[InputRequired(), length( 
        min=4, max=20)], render_kw={"placeholder": "Password"})
  
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")
            

# Login Form

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = StringField(validators=[InputRequired(), length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
  
    submit = SubmitField("Login")
        



#routes
@app.route('/')
def home():
    return render_template('home.html')

#route for the login url will have login 34
# add bcrypt  and import maskpass for encryption and password hashing 
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form = form)

#route for the dashboard. create a current post 
@app.route('/dashboard', methods=['GET','POST'])
# @login_required
def dashboard():
    return render_template('dashboard.html')
    


#route for logout will just redirect for the login
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



#route for the register form add a first name and last name field for good measure 
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('Register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)