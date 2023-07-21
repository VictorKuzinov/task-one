# routes.py
from aiohttp import web
from aiohttp_session import get_session
from auth import *
from db import *
import json
from app import loggin_info, loggin_error

async def login(request):
    data = await request.json()
    login = data.get('Login')
    password = data.get('Password')
    if await check_credentials(login, password) :
        token = await generate_token(login, password)
        response_data = {'token': token}
        response = web.Response(text=json.dumps(response_data, ensure_ascii=False), status=200,content_type='application/json')
        await loggin_info('Учетные данные введены корректно, можно работать...')
        await loggin_info(response_data)
        if login:  # Проверка, что username не является пустой строкой
            await remember(request, response, login)
        return response
    else:
        response_data = {'error': 'Неверные учетные данные'}
        await loggin_error(response_data)
        response = web.Response(text=json.dumps(response_data, ensure_ascii=False), status=401,
                                content_type='application/json')
        await remember(request, response, ' ')
        return response

async def check_permission(request, method, table, records):
    session = await get_session(request)
    allowed_methods = session.get('allowed_methods')
    tables=session.get('tables')
    try:
       userid=session.get('userid')
       user_id = int(request.match_info['user_id'])
    except KeyError:
        user_id=0
        await loggin_error('Ошибка KeyError')
    await loggin_info('Работает функция check_permission()...')
    records = session.get('records')
    if allowed_methods is not None:
        allowed_methods = json.loads(allowed_methods)
        await loggin_info('Доступные методы'+ str(allowed_methods))
    # Проверка разрешений на основе разрешенных методов API и других параметров
    try:
       if method in allowed_methods and table in tables:
          if records:
             # Разрешение для всех записей
             return True
          else:
             try:
                if userid==user_id :
                   # Разрешение только для своей записи
                   return True
                else:
                   return False
             except UnboundLocalError:
                await loggin_error('Ошибка UnboundLocalError:')
                return True
    except TypeError:
        await loggin_error('Ошибка TypeError: Введены некорректные данные в запросе')
        web.Response(
            text=json.dumps({'error': 'Введены некорректные данные в запросе'},
                            ensure_ascii=False), status=400, content_type='application/json')
        return False
    return False

async def update_user(request):
    try:
       user_id = int(request.match_info['user_id'])
       session = await get_session(request)
       records = session.get('records')
       await loggin_info('Это маршрут UPDATE USERS')
       # Проверка разрешений
       if not await check_permission(request,'UPDATE', 'Users', records):
           await loggin_error('Недостаточно прав доступа')
           return web.Response(text=json.dumps({'error': 'Недостаточно прав доступа'}, ensure_ascii=False), status=403, content_type='application/json')
       else:
           # Обновление пользователя в базе данных
           updated = await update_user_in_db(request)

           if updated:
              await loggin_info('message: Пользователь успешно обновлен')
              return web.Response(text=json.dumps({'message': 'Пользователь успешно обновлен'}, ensure_ascii=False), status=201, content_type='application/json')
           else:
              await loggin_error('Не удалось обновить пользователя')
              return web.Response(text=json.dumps({'error': 'Не удалось обновить пользователя'}, ensure_ascii=False), status=404, content_type='application/json')
    except ValueError:
        print('Ошибка ValueError')
        await loggin_error('Введен некорректный UserID в запросе')
        return web.Response(
            text=json.dumps({'error': 'Введен некорректный UserID в запросе'},
                ensure_ascii=False), status=400, content_type='application/json')
async def create_user(request):
    try:
        data = await request.json()
        session = await get_session(request)
        records = session.get('records')
        await loggin_info('Это маршрут CREATE Users')
        userid=None
        # Проверка разрешений
        if not await check_permission(request,'CREATE', 'Users', records):
           await loggin_error('Недостаточно прав доступа')
           return web.Response(text=json.dumps({'error': 'Недостаточно прав доступа'}, ensure_ascii=False), status=403, content_type='application/json')
        # Создание пользователя в базе данных
        user_id = await create_user_in_db(request)
        if not user_id:
           await loggin_error('Пользователь не создан, введите корректные данные')
           return web.Response(text=json.dumps({'error': 'Пользователь не создан, введите корректные данные'}, ensure_ascii=False), status=409,
                   content_type='application/json')
        else:
           last_user_id = await get_last_user_id_from_db(request.app)
           user = {
              'user_id': last_user_id,
              'name': data['Name'],
              'family': data['Family'],
              'login': data['Login'],
              'password': data['Password'],
              'date_birth': data['Date_birth'],
              'date_registr': data['Date_registr'],
              'role_id': data['RoleID']
           }
           await loggin_info(user)
           return web.Response(text=json.dumps(user, ensure_ascii=False), status=200, content_type='application/json')
    except ValueError:
        await loggin_error('Введен некорректный UserID в запросе')
        return web.Response(
            text=json.dumps({'error': 'Введен некорректный UserID в запросе'},
                ensure_ascii=False), status=400, content_type='application/json')
async def get_user(request):
    try:
       user_id = int(request.match_info['user_id'])
       session = await get_session(request)
       records = session.get('records')
       await loggin_info('Это маршрут READ Users')
       # Проверка разрешений
       if not await check_permission(request,'READ', 'Users', records):
           await loggin_error('Недостаточно прав доступа')
           return web.Response(text=json.dumps({'error': 'Недостаточно прав доступа'},
                ensure_ascii=False), status=403, content_type='application/json')

       # Получение пользователя из базы данных
       user_data = await get_user_from_db(request)
       if user_data == {} :
           await loggin_error('Пользователь не найден')
           return web.Response(text=json.dumps({'error': 'Пользователь не найден'},
                ensure_ascii=False), status=404, content_type='application/json')
       else:
           await loggin_info('Пользователь найден: '+str(user_data))
           return web.Response(text=json.dumps({'message': 'Пользователь найден: ', 'user':  user_data}, ensure_ascii=False),
                content_type='application/json')
    except ValueError:
        await loggin_error('Введен некорректный UserID в запросе')
        return web.Response(
            text=json.dumps({'error': 'Введен некорректный UserID в запросе'},
                ensure_ascii=False), status=400, content_type='application/json')
async def delete_user(request):
    try:
        user_id = int(request.match_info['user_id'])
        session = await get_session(request)
        records = session.get('records')
        await loggin_info('Это маршрут DELETE Users')
        # Проверка разрешений
        if not await check_permission(request, 'DELETE', 'Users', records):
            response_data = {'error': 'Недостаточно прав доступа'}
            await loggin_error(response_data)
            return web.Response(text=json.dumps(response_data, ensure_ascii=False), status=403, content_type='application/json')
        # Удаление пользователя из базы данных
        deleted = await delete_user_from_db(request)
        if not deleted:
            response_data = {'error': 'Пользователь не найден'}
            await loggin_error(response_data)
            return web.Response(text=json.dumps(response_data, ensure_ascii=False), status=404, content_type='application/json')
        else:
            response_data = {'message': 'Пользователь удален'}
            await loggin_error(response_data)
            return web.Response(text=json.dumps(response_data, ensure_ascii=False), content_type='application/json')
    except ValueError:
        await loggin_error('Введен некорректный UserID в запросе')
        return web.Response(
            text=json.dumps({'error': 'Введен некорректный UserID в запросе'},
                ensure_ascii=False), status=400, content_type='application/json')
async def update_role(request):
    session = await get_session(request)
    records = session.get('records')
    await loggin_info('Это маршрут Update Roles')
    # Проверка разрешений
    if not await check_permission(request, 'UPDATE', 'Roles', records):
         await loggin_error('Недостаточно прав')
         return web.Response(text=json.dumps({'error': 'Недостаточно прав'},ensure_ascii=False),
                status=403, content_type='application/json')
    else:# Обновление информации о роли
       if await update_role_in_db(request):
           await loggin_info('Роль успешно обновлена')
           return web.Response(text=json.dumps({'message': 'Роль успешно обновлена'}, ensure_ascii=False),
                status=200, content_type='application/json')
       else:
           await loggin_error('Роль не обновлена')
           return web.Response(text=json.dumps({'error': 'Роль не обновлена'}, ensure_ascii=False),
                status=400, content_type='application/json')

async def create_role(request):
    session = await get_session(request)
    records = session.get('records')
    await loggin_info('Это маршрут CREATE Roles')
    data = await request.json()
    # Проверка разрешений
    if not await check_permission(request, 'CREATE', 'Roles', records):
        await loggin_error('Недостаточно прав длступа')
        return web.Response(text=json.dumps({'error': 'Недостаточно прав доступа'},ensure_ascii=False),
                            status=403, content_type='application/json')

    # Создание роли в базе данных
    role_id = await create_role_in_db(request)
    if not role_id:
        await loggin_error('Такая роль уже существует')
        return web.Response(text=json.dumps({'error': 'Такая роль уже существует'}, ensure_ascii=False), status=409,
                            content_type='application/json')
    else:
        role = {
            'user_id': data['RoleID'],
            'allowed_methods': data['Allowed_methods'],
            'tables': data['Tables'],
            'records': data['Records']
        }
        await loggin_info(role)
        return web.Response(text=json.dumps({'role_id': role}), status=200, content_type='application/json')
async def get_role(request):
     session = await get_session(request)
     records = session.get('records')
     await loggin_info('Это маршрут READ Roles')
     # Проверка разрешений
     if not await check_permission(request, 'READ', 'Roles', records):
         await loggin_error('Недостаточно прав доступа')
         return web.Response(
              text=json.dumps({'error': 'Недостаточно прав доступа'}, ensure_ascii=False),
              status=403, content_type='application/json'
         )
        # Получение информации о роли
     role_data = await get_role_from_db(request)
     if not role_data:
         await loggin_error('Роль не найдена')
         return web.Response(
              text=json.dumps({'error': 'Роль не найдена'}, ensure_ascii=False),
              status=404, content_type='application/json'
         )
     else:
         response_data = {'role_id': role_data}
         await loggin_info(role_data)
         return web.Response(
               text=json.dumps(response_data, ensure_ascii=False),
               status=200, content_type='application/json'
         )
async def delete_role(request):
    session = await get_session(request)
    records = session.get('records')
    await loggin_info('Это маршрут DELETE Roles')
    if not await check_permission(request, 'DELETE', 'Roles', records):
        await loggin_error('Недостаточно прав доступа')
        return web.Response(text=json.dumps({'error': 'Недостаточно прав доступа'}, ensure_ascii=False),
                            status=403, content_type='application/json')
    try:
        role_id = request.match_info['role_id']  # Получаем значение role_id из запроса
        if await delete_role_from_db(request, role_id):
            await loggin_info('Роль успешно удалена')
            return web.Response(text=json.dumps({'message': 'Роль успешно удалена'}, ensure_ascii=False),
                                status=200, content_type='application/json')
        else:
            await loggin_info('Роль не найдена')
            return web.Response(text=json.dumps({'message': 'Роль не найдена'}, ensure_ascii=False),
                                status=404, content_type='application/json')
    except Exception as e:
        # Обработка исключения
        await loggin_error('Произошла ошибка при удалении роли, детали'+ str(e))
        return web.Response(text=json.dumps({'error': 'Произошла ошибка при удалении роли', 'details': str(e)},
                            ensure_ascii=False),
                            status=500, content_type='application/json')
def setup_routes(app):
    app.router.add_post('/login', login)
    app.router.add_post('/insert_users', create_user)
    app.router.add_get('/read_users/{user_id}', get_user)
    app.router.add_put('/update_users/{user_id}', update_user)
    app.router.add_delete('/delete_users/{user_id}', delete_user)
    app.router.add_post('/insert_roles', create_role)
    app.router.add_get('/read_roles/{role_id}', get_role)
    app.router.add_put('/update_roles/{role_id}', update_role)
    app.router.add_delete('/delete_roles/{role_id}', delete_role)
