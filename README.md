#### Postik - социальная сеть для публикации личных дневников. 
>Это простой проект, но здесь уже можно читать посты и отправлять собственные записи, подписываться на авторов, оставлять комментарии. Эту основу легко доработать, добавляя новые возможности.
>Проект создан на основе Django с покрытием тестами на 80 % (Django unittest), кэшированием, регистрацией и аутентификацией.

##### Технологии:
+ Django

#### Как запустить проект:

+ клонируем репозиторий `git clone`
`git@github.com:sabina-045/posts.git`
и переходим в него
    + разворачиваем виртуальное окружение
    `python3 -m venv env` (Windows: `python -m venv env`)
    + активируем его
    `source env/bin/activate` (Windows: `source env/scripts/activate`)
    + устанавливаем зависимости из файла requirements.txt
    `pip install -r requirements.txt`
+ выполняем миграции
`python3 manage.py migrate` (Windows: `python manage.py migrate`)
+ запускаем проект
`python3 manage.py runserver` (Windows: `python manage.py runserver).
И вперед!

#### Примеры запросов:

/ - последние посты на сайте

/posts/{post_id}/ - информация об отдельном посте

/posts/{post_id}/edit/ - изменение поста автором

/group/{slug} - список постов группы

/create/ - создание поста

/posts/{post_id}/comment/ - добавление комментария к посту

/follow/ - список авторов, на которых подписался пользователь

/profile/{username}/follow/ - подписаться на автора поста

_По умолчанию к основным действиям доступ только у авторизованных пользователей._

</br>

> Команда создателей:
Яндекс Практикум, Сабина Гаджиева.

