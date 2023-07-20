# app.py
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
    print("Установка CORS...")
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
    print("CORS установка выполнена.")

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