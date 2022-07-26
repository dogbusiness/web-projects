from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import smtplib
from datetime import datetime

# CONSTANTS #
my_email = 'email'
yandex_app_password = '...'
smtp_server = 'smtp.yandex.ru'
subject = 'Кто-то отправил форму на сайте блога'
website_admin_password = 'парольотсайталол'

# Web
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class EditPostForm(FlaskForm):
    password = PasswordField("Admin Password:", validators=[DataRequired()])
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

@app.route('/')
def home():
    posts = db.session.query(BlogPost).order_by(BlogPost.id.desc()).all()
    db.session.commit()
    return render_template("index.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html", form_successful=False)
    elif request.method == 'POST':
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

        return render_template("contact.html", form_successful=True)

@app.route('/post/<int:id>')
def show_post(id):
    posts = db.session.query(BlogPost).order_by(BlogPost.id).all()
    db.session.commit()
    requested_post = None
    for blog_post in posts:
        if blog_post.id == id:
            requested_post = blog_post
    return render_template('post.html', post=requested_post)

@app.route('/edit-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    curr_post = BlogPost.query.get(id)
    edit_form = EditPostForm(
        title=curr_post.title,
        subtitle=curr_post.subtitle,
        img_url=curr_post.img_url,
        author=curr_post.author,
        body=curr_post.body
    )
    if edit_form.validate_on_submit():
        if edit_form.password.data == website_admin_password:
            curr_post.title = edit_form.title.data
            curr_post.subtitle = edit_form.subtitle.data
            curr_post.author = edit_form.author.data
            curr_post.img_url = edit_form.img_url.data
            curr_post.body = edit_form.body.data
            curr_post.date = curr_post.date # Дата не меняется. Сохраняется оригинальная дата создания
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template("make-post.html", form=edit_form, is_edit=True)
    else:
        return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route('/new-post', methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        body = form.body.data
        date = datetime.now().strftime("%d %B, %Y")
        new_post = BlogPost(title=title, subtitle=subtitle, author=author, img_url=img_url, body=body, date=date)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("make-post.html", form=form, is_edit=False)

@app.route('/delete-post/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
    if request.args.get('password') == website_admin_password:
        post_to_delete = BlogPost.query.get(id)
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return jsonify({"result": "Sorry wrong password"}), 403


if __name__ == "__main__":
    app.run(threaded=True, port=5000, debug=False)
    # app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
