from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import sqlmodel 
#import psycopg2

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None

from app.model import SQLModel
from app.config import local_settings

target_metadata = SQLModel.metadata
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

from alembic.autogenerate import renderers
from sqlalchemy import String

@renderers.dispatch_for(sqlmodel.sql.sqltypes.AutoString)
def _render_autostring(type_, autogen_context):
    return "sa.String()"


# Add these imports for proper type handling
from sqlalchemy.dialects import postgresql
from sqlmodel.sql.sqltypes import AutoString

# Add custom type renderers
def render_item(type_, obj, autogen_context):
    if isinstance(type_, AutoString):
        return "sa.String()"
    return False

def get_url():
    """Return the database URL from the settings."""

    #return "postgresql://postgres:postgres@localhost:5433/arxiv_papers"
    return str(local_settings.SQLALCHEMY_DATABASE_URI)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    #url = config.get_main_option("sqlalchemy.url")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_item=render_item, 
        #dialect_opts={"paramstyle": "named"},
        compare_type=True,
        user_module_prefix='sqlmodel.sql.sqltypes.',
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
