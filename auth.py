# auth.py
import jwt
import asyncpg
from aiohttp_security import remember, forget, authorized_userid
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE, SECRET_KEY

async def generate_token(login, password):
    payload = {'Login': login, 'Password': password}
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    token = "Bearer "+ token
    print(token)
    return token

async def check_credentials(login, password):
    conn = await asyncpg.connect(
        host=DB_HOST,
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD
    )
    sql = 'SELECT "RoleID" FROM public."Users" WHERE "Login" = $1 AND "Password"=$2'
    params = (login, password)
    result = await conn.fetchrow(sql, *params)
    await conn.close()

    if result is not None:
        return True  # Запись найдена, возвращаем True
    else:
        return False # Запись не найдена, возвращаем False
