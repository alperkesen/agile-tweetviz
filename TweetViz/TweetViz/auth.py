from flask import render_template, redirect, url_for, request, flash, session
from TweetViz import app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, login_user, logout_user
from .models import User
from . import db
from . import recaptcha

@app.route('/login', methods=['POST'])
def login_post():
    if app.config['TESTING'] == False and not (recaptcha.verify()):
        flash('ReCaptcha verification error!')
        return redirect(url_for('login'))

    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    if len(username) < 3 or len(password) < 3:
        flash('Username & Password is not allowed.')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('home'))


@app.route('/register', methods=['POST'])
def signup_post():
    if app.config['TESTING'] == False and not (recaptcha.verify()):
        flash('ReCaptcha verification error!')
        return redirect(url_for('login'))

    username = request.form.get('username')
    password = request.form.get('password')

    if len(username) < 3 or len(password) < 3:
        flash('Username & Password is not allowed')
        return redirect(url_for('register'))

    user = User.query.filter_by(username=username).first()

    if user:
        return redirect(url_for('register'))

    new_user = User(username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    flash('You can login now with you credentials:')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    try:
        session.pop('data')
    except:
        pass

    logout_user()
    return redirect(url_for('home'))

