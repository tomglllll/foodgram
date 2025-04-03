# Foodgram

**Foodgram** — веб-приложение, в котором пользователи публикуют рецепты, подписываются на любимых авторов, добавляют рецепты в избранное и формируют список покупок с возможностью его скачивания.

## Возможности

### Аутентификация
- Только зарегистрированные пользователи могут:
  - публиковать рецепты;
  - подписываться на авторов;
  - добавлять рецепты в избранное;
  - работать со списком покупок.

### Рецепты
- Публикация рецептов с описанием, изображением, тегами и ингредиентами (указывается количество и единицы измерения).
- Возможность редактирования и удаления собственных рецептов.

### Фильтрация
- Фильтрация рецептов по тегам (множественный выбор, логика "ИЛИ").
- Поддерживается фильтрация в избранном и в списке рецептов определённого пользователя.

### Избранное
- Добавление рецептов в избранное с главной страницы и страницы рецепта.
- Просмотр и удаление избранного.
- Доступ к списку только у владельца.

### Список покупок
- Добавление рецептов в покупки.
- Автоматическая агрегация ингредиентов (например, Сахар — 5 г и 10 г объединяются в 15 г).
- Скачивание списка в `.txt`, `.pdf` или ином формате.
- Удаление рецептов из списка.

### Подписки
- Подписка на авторов с их профиля или рецептов.
- Просмотр новых рецептов от подписок в разделе **Мои подписки**.
- Возможность отписки.

### Смена аватара
- Смена и удаление аватара пользователя.
- Заглушка по умолчанию, если аватар не загружен.

### Смена пароля
- Через выпадающее меню в шапке сайта.

---

## Технологии

- **Backend**: Django, Django REST Framework
- **Frontend**: React (SPA)
- **Database**: PostgreSQL
- **CI/CD**: GitHub Actions
- **Контейнеризация**: Docker, docker-compose
- **Web-сервер**: Nginx

---

## Развертывание на сервере

1. Склонируйте реполиторий
```
git clone https://github.com/tomglllll/foodgram
```

2. Выполните вход на свой удаленный сервер

3. Установите docker и docker-compose:
```
sudo apt update
sudo apt install -y docker.io
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. Создайте и заполните .env файл:
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=
DB_PORT=
SECRET_KEY=""
DEBUG=
ALLOWED_HOSTS=
```

5. Добавьте secrets в github actions:
```
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
SSH_KEY
SSH_PASSPHRASE
TELEGRAM_TO
TELEGRAM_TOKEN
USER
```

6. Соберите проект
```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py collectstatic
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py load_data
sudo docker-compose exec backend python manage.py createsuperuser
```
---

## Домен
https://foodgramdeploy.zapto.org

---

## Автор
@tomglllll в рамках учебного проекта на Яндекс Практикум


