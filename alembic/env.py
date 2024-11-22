import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Local imports
from src.services.database import Base

# Retrieve Alembic configuration
config = context.config

# Configure logging using the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for schema generation
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    # Use DATABASE_URL environment variable if set, otherwise fallback to config.

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    # Use DATABASE_URL environment variable if set, otherwise fallback to config.

    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Determine offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
