from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv() 
# Configuración de la base de datos
DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_URL')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
base = declarative_base()
def get_db():
    connection = sessionLocal()
    try:
        yield connection
    finally:
        connection.close()