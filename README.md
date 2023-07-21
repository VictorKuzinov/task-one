# task-one
Задание по REST API
Табилца Users: (Имя, Фамилия, логин, пароль, дата рождения, дата регистрации, роль)
Таблица Roles: (роли: Admin, User)
Таблица History: (ID, Old, New)
Ртиггер на таблицу Users, который сохраняет все мзменения (Old, New в формате JSON)
Требование к BACKEND:
1. Логирование.
2. Доступ ко всем маршрутам только после авторизации.
3. Подключение "сессий"
4. Администартор выполняет любой метод, с любой таблицей.
Польхователь с таюлицей Users и только со своим аккаунтом
5. Внутри сессиизашиты методы API, которые разрешены к исполнению
6. Возможность использование CRUD не точечно.

Описание основных модулей:
- Модуль app.py
Модуль app.py представляет собой точку входа в приложение.
В нем инициализируется web.Application() и выполняется настройка различных компонентов, таких как Cross-Origin Resource Sharing (CORS), Swagger-документация, сессии, аутентификация и маршруты.
Контекст приложения app используется для хранения объекта базы данных db_object, который инициализируется с помощью функции db.initialize_db(app).
Компоненты приложения, такие как мидлвары и маршруты, добавляются в контекст app.
Модуль содержит две функции для логирования информационных сообщений loggin_info и ошибок loggin_error.
При старте приложения выполняется функция on_startup, которая также выполняет инициализацию базы данных.
Внимание: финальная строка asyncio.run(main()) выполняется только при запуске файла app.py напрямую, она не будет выполнена, если этот файл импортируется как модуль в другой файл.
- Mодуль auth.py
В данном модуле содержатся две функции:

generate_token: Эта функция принимает логин и пароль пользователя, генерирует JWT-токен с помощью библиотеки jwt и возвращает его с префиксом 'Bearer'.

check_credentials: Эта функция проверяет существование учетных данных пользователя в базе данных. Она подключается к базе данных с помощью библиотеки asyncpg, выполняет SQL-запрос для поиска соответствующей записи в таблице "Users", используя переданный логин и пароль. Если запись существует, функция возвращает True, в противном случае возвращает False.





User
Прошу помочь с описанием модуля:                                                                                                        # app.py
import asyncio
import aiohttp_session
import db
import logging
import datetime
from aiohttp import web
import aiohttp_cors
from middlewares import token_verification_middleware
from aiohttp_session import setup as setup_session
from aiohttp_session import SimpleCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import (
    SessionIdentityPolicy,
    AbstractAuthorizationPolicy
)
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from aiohttp_swagger3 import SwaggerDocs, SwaggerInfo, SwaggerUiSettings

async def setup_cors(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        if route.resource.canonical == aiohttp.web_urldispatcher.DynamicResource('/{path_info:.*}').canonical:
            cors.add(route)

def setup_swagger_docs(app):
    # Настройка Swagger-документации
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/api/v1/docs/"),
        info=SwaggerInfo(
            title="Swagger",
            version="1.0.0",
        ),
        components="C:\Python\Task thirteen\static\swagger.json"
    )
class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        return True

    async def authorized_userid(self, identity):
        return 'user123'

async def loggin_info(message) :
    # Получение текущей даты и времени
    current_datetime = datetime.datetime.now()
    # Форматирование даты и времени
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Запись даты и времени в логи
    logging.info(f"{formatted_datetime} >> {message}")

async def loggin_error(message) :
    # Получение текущей даты и времени
    current_datetime = datetime.datetime.now()
    # Форматирование даты и времени
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Запись даты и времени в логи
    logging.error(f"{formatted_datetime} >> {message}")

async def on_startup(app):
    await db.initialize_db(app)

async def init_app():
    from routes import setup_routes
    logging.basicConfig(filename='log.txt', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
    await loggin_info('Старт программы...')
    app = web.Application()
    db_object = await db.initialize_db(app)
    app['db'] = db_object
    await setup_cors(app)
    setup_session(app, aiohttp_session.SimpleCookieStorage())
    app.middlewares.append(token_verification_middleware)
    app.middlewares.append(validation_middleware)
    setup_security(app, SessionIdentityPolicy(), MyAuthorizationPolicy())
    setup_swagger_docs(app)
    setup_routes(app)
    return app

async def main():
    await loggin_info('Окончание работы программы')

if __name__ == '__main__':
    app = init_app()
    #web.run_app(app, host='localhost', port=8080)
    web.run_app(app, host='api', port=8080)
    asyncio.run(main())
ChatGPT
Модуль app.py:

python
Copy code
import asyncio
import logging
import datetime
import aiohttp_session
import aiohttp_cors
from aiohttp import web
from middlewares import token_verification_middleware
from aiohttp_session import setup as setup_session
from aiohttp_session import SimpleCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import (
    SessionIdentityPolicy,
    AbstractAuthorizationPolicy
)
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from aiohttp_swagger3 import SwaggerDocs, SwaggerInfo, SwaggerUiSettings
import db
from routes import setup_routes

async def setup_cors(app):
    # Настройка Cross-Origin Resource Sharing (CORS)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        if route.resource.canonical == aiohttp.web_urldispatcher.DynamicResource('/{path_info:.*}').canonical:
            cors.add(route)

def setup_swagger_docs(app):
    # Настройка Swagger-документации
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/api/v1/docs/"),
        info=SwaggerInfo(
            title="Swagger",
            version="1.0.0",
        ),
        components="C:\Python\Task thirteen\static\swagger.json"
    )

class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        return True

    async def authorized_userid(self, identity):
        return 'user123'

async def loggin_info(message):
    # Запись сообщения в лог с информацией
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"{formatted_datetime} >> {message}")

async def loggin_error(message):
    # Запись сообщения в лог с ошибкой
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    logging.error(f"{formatted_datetime} >> {message}")

async def on_startup(app):
    # Выполняется при старте приложения
    await db.initialize_db(app)

async def init_app():
    logging.basicConfig(filename='log.txt', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
    await loggin_info('Старт программы...')
    app = web.Application()
    db_object = await db.initialize_db(app)
    app['db'] = db_object
    await setup_cors(app)
    setup_session(app, aiohttp_session.SimpleCookieStorage())
    app.middlewares.append(token_verification_middleware)
    app.middlewares.append(validation_middleware)
    setup_security(app, SessionIdentityPolicy(), MyAuthorizationPolicy())
    setup_swagger_docs(app)
    setup_routes(app)
    return app

async def main():
    await loggin_info('Окончание работы программы')

if __name__ == '__main__':
    app = init_app()
    web.run_app(app, host='api', port=8080)
    asyncio.run(main())
Описание функциональности модуля app.py:

Модуль app.py представляет собой точку входа в приложение.
В нем инициализируется web.Application() и выполняется настройка различных компонентов, таких как Cross-Origin Resource Sharing (CORS), Swagger-документация, сессии, аутентификация и маршруты.
Контекст приложения app используется для хранения объекта базы данных db_object, который инициализируется с помощью функции db.initialize_db(app).
Компоненты приложения, такие как мидлвары и маршруты, добавляются в контекст app.
Модуль содержит две функции для логирования информационных сообщений loggin_info и ошибок loggin_error.
При старте приложения выполняется функция on_startup, которая также выполняет инициализацию базы данных.
Внимание: финальная строка asyncio.run(main()) выполняется только при запуске файла app.py напрямую, она не будет выполнена, если этот файл импортируется как модуль в другой файл.
- Модуль routes.py:
Модуль routes.py отвечает за определение и настройку маршрутов (эндпоинтов) в веб-приложении.
В файле определены различные функции-обработчики (хэндлеры) для каждого маршрута.

Функция login отвечает за аутентификацию пользователя и генерацию токена. Она принимает POST-запрос с JSON-данными, содержащими логин и пароль. Затем проверяет учетные данные с помощью функции check_credentials из модуля auth. Если учетные данные верны, генерируется токен с помощью функции generate_token из модуля auth, и пользователю возвращается успешный ответ с токеном в формате JSON. В противном случае возвращается ответ с ошибкой.
Маршруты /insert_users, /read_users/{user_id}, /update_users/{user_id}, /delete_users/{user_id} используются для создания, чтения, обновления и удаления пользователей в базе данных соответственно.
Маршруты /insert_roles, /read_roles/{role_id}, /update_roles/{role_id}, /delete_roles/{role_id} используются для создания, чтения, обновления и удаления ролей в базе данных соответственно.

Функция check_permission отвечает за проверку разрешений пользователя на основе разрешенных методов API и других параметров. Она принимает запрос (request), метод (method), имя таблицы (table) и флаг записей (records). Эта функция используется в различных хэндлерах для проверки разрешений на доступ к определенным эндпоинтам и записям. Здесь мы получаем информацию из сессии пользователя (которая хранится с помощью aiohttp_session), такую как разрешенные методы API (allowed_methods), список разрешенных таблиц (tables) и идентификатор пользователя (userid). Затем функция сравнивает разрешенные методы и таблицы с методом и таблицей запроса и определяет, есть ли у пользователя доступ к этому запросу.
Функции обработчиков используют функции из других модулей auth.py и db.py для выполнения операций аутентификации и работы с базой данных.
Для логирования событий используются функции loggin_info и loggin_error из модуля app.py.
  
