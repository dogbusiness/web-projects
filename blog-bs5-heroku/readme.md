Если еще не убрал с деплоя - https://blog-bs5.herokuapp.com/

Полностью рабочий проект, но для пользования необходимо завести собственный password app в кабинете яндекса для использования smtp в форме обратной связи. Не залиты posts.db, картинки за ненадобностью.

Скрипт, проверяющий пароль при попытке удалить пост на главной странице далек от идеала. Делал как мог на js для "пробы пера".

При деплое возникали проблемы с импортом из jinja. Если вы хотите работающую на heroku jinja, необходимо после использования pipreqs добавить в requirements.txt версию вашей джинджы. Была также ошибка импорта из itsdangerous. Решается указанием конкретной версии в злополучном requirements.txt. Также нужно не забывать указывать версию gunicorn с помощью которого работает Procfile (!)
