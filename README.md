# ИАРА - система за риболовен контрол

Уеб приложение за управление на основни дейности, свързани с риболовен контрол: потребители, риболовни билети, проверки, глоби, разрешителни, съдове и карта на водоемите в България.

Проектът е изграден с Flask, SQLAlchemy, SQLite и стандартни HTML/CSS/JavaScript шаблони. Картата използва Leaflet и OpenStreetMap.

## Функционалности

- Вход и регистрация на потребители.
- Табло за управление със статистики за билети, проверки, разрешителни, съдове и глоби.
- Профил на потребителя с редакция на данни и смяна на парола.
- Проверка на кораб по CFR номер.
- Издаване и история на риболовни билети.
- Записване и преглед на инспекции.
- Издаване, преглед и отбелязване на платени глоби.
- Интерактивна карта на водоеми с риби, сезони и любопитни факти.
- REST API за основните операции.

## Технологии

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- SQLite
- Jinja2 templates
- HTML, CSS, JavaScript
- Leaflet

## Структура на проекта

```text
.
├── app.py                 # Създаване на Flask приложението, база и начални данни
├── config.py              # Настройки за база, secret key и помощни стойности
├── models.py              # SQLAlchemy модели
├── routes.py              # Web страници и API маршрути
├── static/
│   ├── css/styles.css     # Основни стилове
│   └── js/script.js       # Frontend логика
├── templates/
│   ├── base.html          # Основен layout
│   ├── login.html         # Вход
│   ├── register.html      # Регистрация
│   ├── index.html         # Табло
│   ├── profile.html       # Профил
│   ├── map.html           # Карта на водоемите
│   ├── tickets.html       # Риболовни билети
│   └── fines.html         # Глоби
└── README.md
```

## Инсталация

1. Отвори проекта в терминал:

```powershell
cd "c:\Users\Dimitar\OneDrive - Министерство на образованието и науката\Desktop\iara-gdbpzn-DSDimitrov23"
```

2. Създай виртуална среда:

```powershell
python -m venv venv
```

3. Активирай я:

```powershell
.\venv\Scripts\Activate.ps1
```

Ако PowerShell блокира активирането, използвай:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

4. Инсталирай зависимостите:

```powershell
pip install flask flask-sqlalchemy flask-cors sqlalchemy werkzeug
```

## Стартиране

```powershell
python app.py
```

След стартиране приложението е достъпно на:

```text
http://127.0.0.1:5000
```

Началната страница пренасочва към `/login`.

## Тестов потребител

При първо стартиране приложението създава начални данни. Ако базата е празна, се създава администратор:

```text
Потребител: admin
Парола: Admin123!
```

## База данни

По подразбиране SQLite базата се записва в:

```text
%LOCALAPPDATA%\IARA\iara_database.db
```

Можеш да зададеш друга база чрез променливата `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "sqlite:///iara_database.db"
python app.py
```

Приложението автоматично създава таблиците и зарежда начални данни за водоеми, съдове, разрешителни, билети, инспекции и глоби.

## Полезни маршрути

### Страници

```text
/login       - вход
/register    - регистрация
/dashboard   - табло за управление
/profile     - потребителски профил
/map         - карта на водоемите
/tickets     - риболовни билети
/fines       - глоби
```

### API

```text
POST   /api/register
POST   /api/login
POST   /api/logout
GET    /api/me
GET    /api/dashboard_stats
GET    /api/tickets
POST   /api/issue_ticket
GET    /api/rivers
POST   /api/river
GET    /api/river/<id>
GET    /api/check_permit/<cfr>
GET    /api/vessels
POST   /api/vessel
PATCH  /api/vessel/<id>
GET    /api/permits
POST   /api/permit
PATCH  /api/permit/<id>/status
GET    /api/inspections
POST   /api/inspection
GET    /api/fines
POST   /api/issue_fine
POST   /api/fine/<id>/pay
POST   /api/fine/pay
```

## Настройки

Поддържани environment променливи:

```text
DATABASE_URL       - адрес на базата данни
FLASK_SECRET_KEY   - secret key за сесиите
FLASK_DEBUG        - true/false за debug режим
```

Пример:

```powershell
$env:FLASK_DEBUG = "true"
$env:FLASK_SECRET_KEY = "dev-secret"
python app.py
```

## Бележки

- За картата е необходим интернет достъп, защото Leaflet CSS/JS и OpenStreetMap tiles се зареждат от външни адреси.
- Част от API маршрутите изискват активна сесия след вход.
- Ако искаш базата да се създаде наново, спри приложението и изтрий SQLite файла от `%LOCALAPPDATA%\IARA\`.
- В production среда смени стойността на `FLASK_SECRET_KEY` и не използвай тестовата парола.
