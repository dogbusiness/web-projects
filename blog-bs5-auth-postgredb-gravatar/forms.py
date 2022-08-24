from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("* Заголовок поста", validators=[DataRequired()])
    subtitle = StringField("* Подзаголовок поста", validators=[DataRequired()])
    img_url = StringField("Картинка на фоне", validators=[])
    body = CKEditorField("* Содержимое", validators=[DataRequired()])
    submit = SubmitField("Запостить")

class CreateUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")

class LoginUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")

class CommentForm(FlaskForm):
    comment = CKEditorField("Комментарий", validators=[DataRequired()])
    submit = SubmitField("Комментировать")