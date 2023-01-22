This is an improved blog-bs5-heroku blog https://blog-auth-bs5.herokuapp.com/

Added login and registration. Ability to comment on posts, edit and delete your posts. During the deployment, there was a difficulty with moving from SQLite to postgresql. Sqlalchemy does not support the "postgres://" dialect (default in heroku). So in the virtual variable you need to replace it with "postgresql://"

-----------------------------------------------------------------------------

Это усовершенствованный блог blog-bs5-heroku
https://blog-auth-bs5.herokuapp.com/

Добавлен логин и регистрация. Возможность комментировать посты, редактировать и удалять свои посты.
При деплое возникла сложность с переездом с SQLite на postgresql. Sqlalchemy не поддерживает диалект "postgres://" (по-умолчанию в heroku). Так что в виртуальной
переменной необходимо заменять на "postgresql://"
