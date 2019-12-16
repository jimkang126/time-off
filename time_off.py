from flask import Flask, flash, redirect, url_for, request, render_template, session, Markup
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import coordinates_api
import hotel_api
import skyscanner_api

app = Flask(__name__)
app.config['SQLACHEMY_DATABASE_URI'] = 'sqlite:///time_off.db'
db = SQLAlchemy(app)

# Global variables
CURRENT_URL = ""
CURRENT_EMAIL = ""
HOTEL_OPTIONS = []
FLIGHT_OPTIONS = []


# User Class
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(45))
    lastname = db.Column(db.String(45))
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String)

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Home Page
@app.route('/', methods=['GET', 'POST'])
def home():
    session["logged_in"] = False
    return render_template('base.html')

# User
@app.route('/user', methods=['GET', 'POST'])
def user(encrypt=None):
    print("Loading User Page")
    session["logged_in"] = True
    user_data = User.query.filter_by(email=CURRENT_EMAIL).first()
    full_name = user_data.firstname + " " + user_data.lastname
    global CURRENT_URL
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('user.html', name = full_name)

# Being Planning Your Trip
@app.route('/begin_planning', methods=['GET', 'POST'])
def plan(encrypt=None):
    session["planning"] = True
    print('Starting to Plan')
    global HOTEL_OPTIONS
    global FLIGHT_OPTIONS
    if request.method == 'POST':
        try:
            origin = request.form.get('origin')
            destination = request.form.get('destination')
            departure_date = request.form.get('departureDate')
            return_date = request.form.get('returnDate')
            key = skyscanner_api.get_key(origin, destination, departure_date, return_date)
            FLIGHT_OPTIONS = skyscanner_api.flight_info(key)
            c_locate = coordinates_api.coordinates(destination)
            c_lat = c_locate['latitude']
            c_lng = c_locate['longitude']
            HOTEL_OPTIONS = hotel_api.hotel(c_lat, c_lng)
            return redirect(url_for('options'))
        except:
            message = Markup("Invalid Information")
            flash(message)
            return render_template('plan.html')
    return render_template('plan.html')


# Trip options
@app.route('/options', methods=['GET', 'POST'])
def options():
    print('Choose your plan')
    if request.method == 'GET':
        return render_template('options.html', hotel_options=HOTEL_OPTIONS, flight_options=FLIGHT_OPTIONS)
    return render_template('options.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            new_user = User(firstname=str.capitalize(request.form['firstname']), lastname=str.capitalize(request.form['lastname']), email=request.form['email'], password=request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            message = Markup("Account already exists!")
            flash(message)
            return render_template('signup.html')
    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    global CURRENT_URL
    global CURRENT_EMAIL
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if session["logged_in"]:
            return redirect(url_for('user', encrypt=CURRENT_URL))
        post_email = request.form['email']
        post_password = request.form['password']
        CURRENT_EMAIL = post_email
        try:
            data = User.query.filter_by(email=post_email).first()
            if data is not None:
                if check_password_hash(data.password, post_password):
                    url = post_email
                    CURRENT_URL = url
                    session["logged_in"] = True
                    return redirect(url_for('user', encrypt=url))
                else:
                    message = Markup("Invalid Email or Password")
                    flash(message)
                    return render_template('login.html')
            else:
                message = Markup("Account does not exist")
                flash(message)
                return render_template('login.html')
        except:
            message = Markup("Login Failed. Please try again.")
            flash(message)
            return render_template('login.html')
    return render_template('login.html')


# Logout
@app.route("/logout")
def logout():
    global CURRENT_URL
    global CURRENT_EMAIL
    session["logged_in"] = False
    CURRENT_URL = ""
    CURRENT_EMAIL = ""
    return redirect(url_for('home'))


if __name__ == "__main__":
    print("App Started!")
    db.create_all()
    app.secret_key = '123'
    app.debug = True
    app.run(threaded=True)
