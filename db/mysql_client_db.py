import os
from dotenv import load_dotenv
from models.mysql import MySQL
from sqlmodel import create_engine

load_dotenv()

db_settings: MySQL = MySQL(
    server=os.getenv('DB_MYSQL_SERVER'),
    port=int(os.getenv('DB_MYSQL_PORT')),
    user=os.getenv('DB_MYSQL_USER'),
    password=os.getenv('DB_MYSQL_PASSWORD'),
    data_base=os.getenv('DB_MYSQL_DB'),
    url='',
)

db_settings.url = f'mysql+pymysql://{db_settings.user}:{db_settings.password}@{db_settings.server}:{db_settings.port}/{db_settings.data_base}'

print(db_settings.url)

db_engine = create_engine(
    url=db_settings.url,
    pool_pre_ping=True,
    future=True,
)