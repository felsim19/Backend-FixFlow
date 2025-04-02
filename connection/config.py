from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "mysql+mysqlconnector://db_admin:admin_adso*@192.168.100.6:3306/fixflow"
engine = create_engine(DB_URL)
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
base = declarative_base()
def get_db():
    connection = sessionLocal()
    try:
        yield connection
    finally:
        connection.close()