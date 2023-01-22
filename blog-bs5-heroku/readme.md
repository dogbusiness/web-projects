If not yet removed from deployment - https://blog-bs5.herokuapp.com/

A fully working project, but to use it, you need to create your own password app in the Yandex account to use smtp in the feedback form. posts.db, pictures aren't uploaded.

The script that checks the password when trying to delete a post on the main page is far from ideal. I did my best on js just for a "pen test".

During the deployment, there were problems with importing from jinja. If you want a jinja that works on heroku, you need to add the version of your jinja to requirements.txt after using pipreqs. There was also an import error from itsdangerous. Solved by specifying a specific version in the ill-fated requirements.txt. You also need to remember to specify the version of gunicorn with which the Procfile works (!)

-------------------------------------------------------------

Если еще не убрал с деплоя - https://blog-bs5.herokuapp.com/

Полностью рабочий проект, но для пользования необходимо завести собственный password app в кабинете яндекса для использования smtp в форме обратной связи. Не залиты posts.db, картинки за ненадобностью.

Скрипт, проверяющий пароль при попытке удалить пост на главной странице далек от идеала. Делал как мог на js для "пробы пера".

При деплое возникали проблемы с импортом из jinja. Если вы хотите работающую на heroku jinja, необходимо после использования pipreqs добавить в requirements.txt версию вашей джинджы. Была также ошибка импорта из itsdangerous. Решается указанием конкретной версии в злополучном requirements.txt. Также нужно не забывать указывать версию gunicorn с помощью которого работает Procfile (!)

