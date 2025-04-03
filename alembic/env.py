from logging.config import fileConfig
from connection.config import base
import os
import sys
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# Añade el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carga las variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuración de Alembic
config = context.config

# Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importa tu Base declarativa
target_metadata = base.metadata

def get_database_url():
    """Construye la URL de conexión desde variables de entorno"""
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_url = os.getenv("DB_URL")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    return f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_url}:{db_port}/{db_name}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()