from flask import Flask, request, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, CreateUserForm, LoginUserForm, CommentForm
import smtplib
import os

# SMTP CONSTANTS #
my_email = os.environ.get('my_email')
yandex_app_password = os.environ.get('yandex_app_password')
smtp_server = 'smtp.yandex.ru'
subject = 'Кто-то отправил форму на сайте блога'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

## CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return UserTable.query.get(int(user_id))

## CONFIGURE TABLES
class UserTable(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # Связь одного ко многим
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("CommentTable", back_populates="comment_author")

class CommentTable(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, ForeignKey('user.id'))
    comment_author = relationship("UserTable", back_populates="comments")
    post_id = db.Column(db.Integer, ForeignKey('blog_posts.id'))
    parent_post = relationship("BlogPost", back_populates="")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Связь одного ко многим
    author_id = db.Column(db.Integer, ForeignKey('user.id'))
    author = relationship("UserTable", back_populates="posts")
    #
    comments = relationship("CommentTable", back_populates="parent_post")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

## GRAVATARS
gravatar = Gravatar(app, size=300, rating='pg', default='retro',
                    force_default=False, force_lower=False, use_ssl=False, base_url=None)

@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).order_by(BlogPost.id.desc()).all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = CreateUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        new_user = UserTable.query.filter_by(email=email).first()
        if new_user is None:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = UserTable(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash("Простите. Такой пользователь уже существует.")
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginUserForm()
    if request.method == "POST":
        email = form.email.data
        password = form.password.data
        user_to_check = UserTable.query.filter_by(email=email).first()
        if user_to_check is not None:
            if check_password_hash(pwhash=user_to_check.password, password=password):
                login_user(user_to_check)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Неправильный пароль")
        else:
            flash("Неправильный email")
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    requested_comments = CommentTable.query.filter_by(post_id=post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Нужно войти в профиль, чтобы комментировать")
            return redirect(url_for("login"))
        new_comment = CommentTable(
            text=form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return render_template("post.html", post=requested_post, logged_in=current_user.is_authenticated,
                               form=form, comments=requested_comments)
    return render_template("post.html", post=requested_post, logged_in=current_user.is_authenticated,
                           form=form, comments=requested_comments)


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "GET":
        return render_template("contact.html", logged_in=current_user.is_authenticated)
    elif request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        # SMTP #
        connection = smtplib.SMTP(smtp_server)
        connection.starttls()
        connection.login(user=my_email, password=yandex_app_password)
        letter = f'Name: {name}\nEmail:{email}\nPhone:{phone}\nMessage:{message}'
        connection.sendmail(from_addr=my_email,
                            to_addrs='sergeusprecious@gmail.com',
                            msg=f'From:{my_email}\n\n\n{letter}')
        flash("Сообщение отправлено")
        return render_template("contact.html", logged_in=current_user.is_authenticated)




@app.route("/new-post", methods=["POST", "GET"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Нужно войти в профиль, чтобы постить")
            return redirect(url_for("login"))
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = post.author
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, logged_in=current_user.is_authenticated, is_edit=True)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    # Нам нужен трай, потому что незалогиненные пользователи могут попробовать вбить ендпоинт вручную
    try:
        if current_user.id != post_to_delete.author_id and current_user.id != 1 or current_user.id is None:
            return abort(403)
        else:
            post_to_delete = BlogPost.query.get(post_id)
            db.session.delete(post_to_delete)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    except AttributeError:
        return abort(403)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(threaded=True, port=5000, debug=False)
