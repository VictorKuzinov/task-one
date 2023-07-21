#env.py
from sqlalchemy import engine_from_config, MetaData
from alembic import context

# Это будет вызываться Alembic сценарием для каждого шага миграции.
# Здесь мы инициализируем подключение к базе данных на основе параметров из конфигурации env.py.

# Создаем подключение к базе данных
# Значения username, password, localhost, db_name, представляют собой параметры подключения к вашей базе данных, 
# и они должны быть заменены на соответствующие значения, которые применимы к вашей базе данных
url = f"postgresql://username:password@localhost/db_name" 

engine = engine_from_config(context.config.get_section('alembic'), url=url)

# Привязываем подключение к контексту
connection = engine.connect()

# Создаем объект MetaData и связываем его с контекстом
metadata = MetaData()
metadata.bind = engine

# Связывание объекта MetaData с контекстом
context.configure(
    connection=connection,
    target_metadata=metadata
)

# Применяем миграции к базе данных, используя созданное подключение
def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Применяем миграции к базе данных, используя созданное подключение
def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=metadata  # Use the same 'metadata' object here
        )

        with context.begin_transaction():
            context.run_migrations()

# В зависимости от окружения, вызываем соответствующую функцию применения миграций
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
