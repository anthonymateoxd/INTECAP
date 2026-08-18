from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.database.base import Base

# Importar todos los modelos para registrar sus tablas en Base.metadata.
from app.modules.users import model as users_model  # noqa: F401
from app.modules.vehicles import model as vehicles_model  # noqa: F401
from app.modules.commissions import model as commissions_model  # noqa: F401
from app.modules.trips import model as trips_model  # noqa: F401
from app.modules.fuel import model as fuel_model  # noqa: F401
from app.modules.maintenance import models as maintenance_models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
