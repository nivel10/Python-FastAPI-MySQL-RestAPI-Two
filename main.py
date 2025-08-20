import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import FastAPI, Depends
from models.mysql import MySQL
from sqlmodel import create_engine, SQLModel, Session, Field

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
# print(db_settings.url)

db_engine = create_engine(
    url=db_settings.url,
    pool_pre_ping=True,
    future=True,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)

def get_session():
    with Session(db_engine) as session:
        yield session

session_dep = Annotated[Session, Depends(get_session)]

#region classes
class HeroBase(SQLModel):
     name: str = Field(index=True)
     age: int | None = Field(default=None, index=True)

class Hero(HeroBase):
     id: int = Field(default=None, primary_key=True)
     secret_name: str

class HeroPublic(HeroBase):
     id: int

class HeroCreate(HeroBase):
     secret_name: str

class HeroUpdate(HeroBase):
     name: str | None = None
     age: int | None = None
     secret_name: str | None = None
#endregion classes

app = FastAPI()

@app.get('/')
async def main():
        with db_engine.connect() as conn:
            return {'section': 'main'}