# task-one
Задание по REST API
Таблица Users: (Имя, Фамилия, логин, пароль, дата рождения, дата регистрации, роль)
Таблица Roles: (Роли: Admin, User)
Таблица History: (ID, Old, New)
Триггер на таблицу Users, который сохраняет все мзменения (Old, New в формате JSON)
Требование к BACKEND:
1. Логирование.
2. Доступ ко всем маршрутам только после авторизации.
3. Подключение "сессий"
4. Администартор выполняет любой метод, с любой таблицей.
Пользователь с таюлицей Users и только со своим аккаунтом
5. Внутри сессии зашиты методы API, которые разрешены к исполнению
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

- Модуль routes.py:
Модуль routes.py отвечает за определение и настройку маршрутов (эндпоинтов) в веб-приложении.
В файле определены различные функции-обработчики (хэндлеры) для каждого маршрута.

Функция login отвечает за аутентификацию пользователя и генерацию токена. Она принимает POST-запрос с JSON-данными, содержащими логин и пароль. Затем проверяет учетные данные с помощью функции check_credentials из модуля auth. Если учетные данные верны, генерируется токен с помощью функции generate_token из модуля auth, и пользователю возвращается успешный ответ с токеном в формате JSON. В противном случае возвращается ответ с ошибкой.
Маршруты /insert_users, /read_users/{user_id}, /update_users/{user_id}, /delete_users/{user_id} используются для создания, чтения, обновления и удаления пользователей в базе данных соответственно.
Маршруты /insert_roles, /read_roles/{role_id}, /update_roles/{role_id}, /delete_roles/{role_id} используются для создания, чтения, обновления и удаления ролей в базе данных соответственно.

Функция check_permission отвечает за проверку разрешений пользователя на основе разрешенных методов API и других параметров. Она принимает запрос (request), метод (method), имя таблицы (table) и флаг записей (records). Эта функция используется в различных хэндлерах для проверки разрешений на доступ к определенным эндпоинтам и записям. Здесь мы получаем информацию из сессии пользователя (которая хранится с помощью aiohttp_session), такую как разрешенные методы API (allowed_methods), список разрешенных таблиц (tables) и идентификатор пользователя (userid). Затем функция сравнивает разрешенные методы и таблицы с методом и таблицей запроса и определяет, есть ли у пользователя доступ к этому запросу.
Функции обработчиков используют функции из других модулей auth.py и db.py для выполнения операций аутентификации и работы с базой данных.
Для логирования событий используются функции loggin_info и loggin_error из модуля app.py.
  
- Модль db.py
Модуль db.py содержит функции для взаимодействия с базой данных. В данном модуле используется библиотека asyncpg, которая обеспечивает асинхронное взаимодействие с PostgreSQL.

get_last_user_id_from_db(app): Эта функция получает максимальный идентификатор пользователя из таблицы "Users" в базе данных. app - это объект приложения aiohttp, который содержит подключение к базе данных в своем поле "db".

update_user_in_db(request): Эта функция отвечает за обновление данных пользователя в таблице "Users". Она получает идентификатор пользователя из URL и JSON-данные запроса. Затем она извлекает существующие данные пользователя из базы данных и обновляет только те поля, которые предоставлены в JSON-данных. После этого выполняется SQL-запрос на обновление данных пользователя в базе данных.

create_user_in_db(request): Эта функция создает нового пользователя в таблице "Users". Она получает JSON-данные запроса, преобразует даты рождения и регистрации в соответствующие объекты типа date, а затем выполняет SQL-запрос на вставку нового пользователя в базу данных.

delete_user_from_db(request): Эта функция удаляет пользователя из таблицы "Users". Она получает идентификатор пользователя из URL и выполняет несколько SQL-запросов, чтобы удалить пользователя и связанные с ним записи из другой таблицы.

get_user_from_db(request): Эта функция получает данные пользователя из таблицы "Users" по его идентификатору. Она также преобразует даты рождения и регистрации в строки в формате 'YYYY-MM-DD'.

create_role_in_db(request): Эта функция создает новую роль в таблице "Roles". Она получает JSON-данные запроса и выполняет SQL-запрос на вставку новой роли в базу данных.

get_role_from_db(request): Эта функция получает данные роли из таблицы "Roles" по её идентификатору. Она возвращает данные роли в виде словаря.

update_role_in_db(request): Эта функция обновляет данные роли в таблице "Roles". Она получает JSON-данные запроса и выполняет SQL-запросы на обновление роли и обновление всех пользователей, связанных с данной ролью.

delete_role_from_db(request, role_id): Эта функция удаляет роль из таблицы "Roles". Она получает идентификатор роли и выполняет SQL-запрос на удаление роли из базы данных.

Каждая функция взаимодействует с базой данных через асинхронное подключение (await app['db'].acquire() as conn) и использует SQL-запросы для выполнения операций в базе данных. В конце каждой функции соединение с базой данных закрывается (await conn.close()).
async def connect_to_db(): Эта функция создает асинхронный пул подключений к базе данных с помощью asyncpg.create_pool(). Она использует параметры подключения, которые определены в файле config.py (DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE, DB_PORT). Пул подключений используется для обеспечения эффективного многопоточного доступа к базе данных.

async def setup_db(connection): Эта функция отвечает за настройку базы данных. Она проверяет, существуют ли таблицы "Roles", "Users" и "History". Если таблицы не существуют, то они создаются с помощью SQL-запросов. Затем функция заполняет таблицу "Roles" двумя ролями: "Admin" и "User", а также создает запись "Admin" в таблице "Users".

async def initialize_db(app): Эта функция используется для инициализации базы данных при запуске приложения. Она вызывает функции connect_to_db() и setup_db() для создания пула подключений и настройки базы данных. После инициализации базы данных, пул подключений возвращается и сохраняется в объекте приложения app, чтобы другие функции приложения могли использовать его для обращения к базе данных.

В функции setup_db(connection), после создания таблицы "History", создается триггерная функция public.users_history_trigger(). Эта функция отслеживает изменения в таблице "Users" и записывает старые и новые значения в таблицу "History". Затем создается триггер users_history для таблицы "Users", который вызывает триггерную функцию public.users_history_trigger() после каждой операции вставки, обновления или удаления записи в таблице "Users". Это позволяет отслеживать историю изменений пользователей.

После выполнения всех действий по инициализации базы данных, возвращается объект пула подключений, который затем используется в основном приложении для взаимодействия с базой данных. Это обеспечивает правильное подключение и конфигурирование базы данных перед запуском сервера.

Документирование REST API, осуществляется с помощью модуля Swagger UI, расположен по адресу: http://api:8080/api/v1/docs/, где задокументирваны все вышеперечисленны методы Rest API, файл swagger.json расположен в папке static.

Кроме этого в проекте используется модуль config.py, в котором описаны прерменные для подключения к базе Postgres и ключ шифрования.
Этот файл config.py содержит параметры конфигурации, которые используются при запуске и настройке приложения. Он позволяет легко изменять значения параметров в одном месте, без необходимости внесения изменений в код приложения:

DB_HOST: Это переменная, которая содержит хост (адрес) базы данных PostgreSQL, к которой приложение будет подключаться. В данном случае, установлено значение 'localhost', что означает, что база данных находится на том же компьютере, где запущено приложение.

- DB_PORT: Это переменная, которая содержит порт, на котором работает база данных PostgreSQL. В данном случае, установлено значение 5432, что является стандартным портом для PostgreSQL.

- DB_USER: Это переменная, которая содержит имя пользователя, используемого для подключения к базе данных PostgreSQL.

- DB_PASSWORD: Это переменная, которая содержит пароль пользователя для подключения к базе данных PostgreSQL.

- DB_DATABASE: Это переменная, которая содержит название базы данных PostgreSQL, с которой приложение будет работать. В данном случае, установлено значение.

- DATABASE_URL: Это переменная, которая содержит URL-адрес базы данных. В данном случае, используется PostgreSQL и соблюдается следующий формат URL: 'postgresql://<username>:<password>@<host>/<database_name>'.

- HOST: Это переменная, которая содержит порт, на котором будет запущен веб-сервер приложения. В данном случае, установлено значение 8080.

- SECRET_KEY: Это переменная, которая содержит секретный ключ для обеспечения безопасности веб-приложения. Этот ключ используется, например, для подписывания и проверки токенов аутентификации, значение должно быть сложным и уникальным.
