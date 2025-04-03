import os
import sys
from dotenv import load_dotenv
from main import app
from sqlalchemy import engine_from_config, pool
from alembic import context

# Configuración básica de logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Añade el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carga variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Importa tu Base declarativa
# Opción 1: Si está en connection/config.py
from connection.config import base

# Opción 2: Si está en main.py
# from main import Base 

target_metadata = base.metadata

def get_database_url():
    """Construye la URL de conexión desde variables de entorno"""
    return f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_URL')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def run_migrations_offline():
    """Ejecuta migraciones en modo offline."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecuta migraciones en modo online."""
    configuration = {
        'sqlalchemy.url': get_database_url()
    }
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