from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required

from flaskblog import db, bcrypt
from .forms import (RegistrationForm, LoginForm,
                             UpdateAccountForm, RequestResetForm,
                             ResetPasswordForm)
from flaskblog.models import User, Post
from ..utils import image_upload, send_reset_email

from flask import Blueprint

users = Blueprint('users', __name__)


PROFILE_PIC_PATH = 'static/images/profile_pics'
POST_PIC_PATH = 'static/images/post_pics'
PROFILE_PIC_SIZE = (125, 125)
POST_THUMB_SIZE = (225, 150)
POST_IMG_SIZE = (500, 300)


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.image.data:
            profile_image = image_upload(
                                         form.image.data,
                                         PROFILE_PIC_PATH,
                                         PROFILE_PIC_SIZE)
            current_user.image_file = profile_image

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')

        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    user_img = url_for('static',
                       filename='images/profile_pics/' + current_user.image_file)
    return render_template('account.html',
                           title='Account',
                           form=form,
                           user_img=user_img)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! You can now log in!', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful. \
                  Please check email and password.', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.post_date.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', user=user, posts=posts)


@users.route("/reset_password", methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instruction to reset your password.', 'success')
        return redirect(url_for('users.login'))

    return render_template('password_reset_request.html', form=form, title='Request Password Reset')


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('users.password_reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        flash(f'Your password has been updated! You can now log in!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password.html', form=form, title='Reset Password')
