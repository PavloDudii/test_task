from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

fileConfig(config.config_file_name)

url = "postgresql+psycopg2://bookuser:bookpass@db:5432/bookdb"
if url:
    config.set_main_option("sqlalchemy.url", url)

target_metadata = None

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
