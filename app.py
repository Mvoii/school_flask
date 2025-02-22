from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from models import User, Contact
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    MONGO_URI=os.getenv('MONGO_URI'),
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('EMAIL_USER'),
    MAIL_PASSWORD=os.getenv('EMAIL_PASS')
)

# Initialize extensions
login_manager = LoginManager(app)
mail = Mail(app)

# MongoDB setup
client = MongoClient(app.config['MONGO_URI'])
db = client.contact_app
users_collection = db.users
contacts_collection = db.contacts

@login_manager.user_loader
def load_user(email):
    user_data = users_collection.find_one({'email': email})
    if not user_data:
        return None
    return User(email=user_data['email'], password=user_data['password'])

# Routes will be added here
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = users_collection.find_one({'email': email})
        
        if user_data and User(email, user_data['password']).verify_password(password):
            user = User(email=email)
            login_user(user)
            return redirect(url_for('contact_form'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users_collection.find_one({'email': email}):
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(email, password)
        users_collection.insert_one({
            'email': new_user.email,
            'password': new_user.password
        })
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user_data = users_collection.find_one({'email': email})
        if user_data:
            user = User(email=user_data['email'])
            token = user.get_reset_token()
            users_collection.update_one(
                {'email': email},
                {'$set': {'reset_token': token}}
            )
            
            msg = Message('Password Reset Request',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f'''To reset your password, visit:
{url_for('reset_password', token=token, _external=True)}

This link expires in 30 minutes.'''
            mail.send(msg)
            flash('Reset instructions sent to your email', 'info')
        else:
            flash('Email not found', 'danger')
    return render_template('forgot_password.html')

# Reset Password Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = User.verify_reset_token(token)
    if not email:
        flash('Invalid/expired token', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pw = generate_password_hash(new_password)
        users_collection.update_one(
            {'email': email},
            {'$set': {'password': hashed_pw}, '$unset': {'reset_token': 1}}
        )
        flash('Password updated! Please login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

# Contact Form Route
@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact_form():
    if request.method == 'POST':
        contact = Contact(
            mobile=request.form['mobile'],
            email=request.form['email'],
            address=request.form['address'],
            reg_number=request.form['reg_number']
        )
        contacts_collection.insert_one(contact.__dict__)
        flash('Contact saved successfully', 'success')
        return redirect(url_for('contact_form'))
    return render_template('contact_form.html')

# Search Route
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        reg_number = request.form['reg_number']
        contact = contacts_collection.find_one({'reg_number': reg_number})
        return render_template('search_results.html', contact=contact)
    return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True, port=5050)
