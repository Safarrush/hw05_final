Социальная сеть YaTube для публикации постов и картинок (Яндекс.Практикум)
=====

Описание проекта
----------
Проект создан в рамках учебного курса Яндекс.Практикум.

Социальная сеть для авторов и подписчиков. Пользователи могут подписываться на избранных авторов, оставлять и удалять комментари к постам, оставлять новые посты на главной странице и в тематических группах, прикреплять изображения к публикуемым постам. 

Проект реализован на MVT-архитектуре, реализована система регистрации новых пользователей, восстановление паролей пользователей через почту, система тестирования проекта на unittest, пагинация постов и кэширование страниц. Проект имеет верстку с адаптацией под размер экрана устройства пользователя.

Системные требования
----------
* Python 3.8+
* Works on Linux, Windows, macOS, BSD

Стек технологий
----------
* Python 3.8
* Django 2.2 
* Unittest
* Pytest
* SQLite3
* CSS
* JS
* HTML

Установка проекта из репозитория (Linux и macOS)
----------

1. Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:Safarrush/hw05_final.git

cd YaTube
```
2. Cоздать и активировать виртуальное окружение:
```bash
python3 -m venv venv

source env/bin/activate
```
3. Установить зависимости из файла ```requirements.txt```:
```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
4. Выполнить миграции:
```bash
cd hw05_final

python3 manage.py migrate
```
5. Запустить проект (в режиме сервера Django):
```bash
python3 manage.py runserver
```
Что могут делать пользователи:
----------
Залогиненные пользователи могут:

1. Просматривать, публиковать, удалять и редактировать свои публикации;
2. Просматривать информацию о сообществах;
3. Просматривать и публиковать комментарии от своего имени к публикациям других пользователей (включая самого себя), удалять и редактировать свои комментарии;
4. Подписываться на других пользователей и просматривать свои подписки.
5. Примечание: Доступ ко всем операциям записи, обновления и удаления доступны только после аутентификации и получения токена.

Анонимные пользователи могут:

1. Просматривать публикации;
2. Просматривать информацию о сообществах;
3. Просматривать комментарии;

Набор доступных эндпоинтов:
----------

1. posts/ - Отображение постов и публикаций (GET, POST);
2. posts/{id} - Получение, изменение, удаление поста с соответствующим id (GET, PUT, PATCH, DELETE);
3. posts/{post_id}/comments/ - Получение комментариев к посту с соответствующим post_id и публикация новых комментариев(GET, POST);
4. posts/{post_id}/comments/{id} - Получение, изменение, удаление комментария с соответствующим id к посту с соответствующим post_id (GET, PUT, PATCH, DELETE);
5. posts/groups/ - Получение описания зарегестрированных сообществ (GET);
6. posts/groups/{id}/ - Получение описания сообщества с соответствующим id (GET);
7. posts/follow/ - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (GET, POST).

Автор:
----------
Рушан - tg @safa_ru
