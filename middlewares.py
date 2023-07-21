# middlewares.py
import json
from aiohttp import web
from aiohttp_session import get_session
from aiohttp_jwt import JWTMiddleware
import jwt
from config import SECRET_KEY

async def token_verification_middleware(app, handler):
    async def middleware(request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Выполнить проверку токена
            try:
                decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request['user'] = decoded_token

                # Получение данных сессии из базы данных или другого источника
                session = await get_session_data(request, decoded_token)
                # Сохранение данных сессии в запросе
                request['session'] = session
            except jwt.DecodeError:
                response_data = {'error': 'Неправильный токен'}
                return web.Response(text=json.dumps(response_data, ensure_ascii=False), status=401,
                                    content_type='application/json')

        return await handler(request)

    return middleware


async def get_session_data(request, decoded_token):
    # Создание сессии
    login = decoded_token.get('Login')
    password = decoded_token.get('Password')
    # Реализуем здесь логику получения данных сессии на основе имени пользователя
    # и возврат соответствующих данных из сессии
    async with request.app['db'].acquire() as conn:
        session_data = await get_session(request)
        session_data.clear()
        user = await conn.fetchrow(
           'SELECT * FROM public."Users" WHERE "Login" = $1 and "Password"=$2',
            login, password
        )
        if user :
            session_data['userid'] = user[0]   # UserID
            session_data['username'] = user[1] # Users.Name
            session_data['login'] = user[3]    # User.Login
            session_data['role'] = user[7]     # Users.RoleID
            role = await conn.fetchrow(
                'SELECT * FROM public."Roles" WHERE "RoleID" = $1',
                 user[7]
            )
            session_data['allowed_methods'] = role[1]  # Roles.Allowed_metod
            session_data['tables'] = role[2]           # Roles.Tables
            session_data['records'] = role[3]          # Roles.Records
    return session_data
