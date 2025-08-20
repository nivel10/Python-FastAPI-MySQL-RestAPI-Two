import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status, Query
from models.mysql import MySQL
from sqlmodel import create_engine, SQLModel, Session, Field, select

load_dotenv()

#region db setting
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
#endregion db settings

#region classes
class HeroBase(SQLModel):
     name: str = Field(index=True)
     age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
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

#region API - paths
@app.get('/', tags=['main'])
async def main():
        with db_engine.connect() as conn:
            return {'section': 'main'}
        
@app.on_event('startup')
async def on_startup():
    try:
        create_db_and_tables()
    except Exception as ex:
        print(str(ex))

@app.post('/heroes/', tags=['heroes'], response_model=HeroPublic)
async def create_hero(hero: HeroCreate, session: session_dep):
     try:
          db_hero = Hero.model_validate(hero)
          session.add(db_hero)
          session.commit()
          session.refresh(db_hero)
          return db_hero
     except Exception as ex:
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=str(ex)
        )
     
@app.get('/heroes/', tags=['heroes'], response_model=list[HeroPublic])
async def get_heroes(
     session: session_dep,
     offset: int = 0,
     limit: Annotated[int, Query(le=100)] = 100,
):
     try:
          heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
          return heroes
     except Exception as ex:
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=str(ex),
          )

@app.get('/heroes/{id}', tags=['heroes'], response_model=HeroPublic)
async def get_heroes(id: int, session: session_dep):
     try:
          hero = session.get(Hero, id)
          if not hero:
               raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Hero not found. id: {id}'
               )
          return hero
     except Exception as ex:
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=str(ex),
          )
#endregion API paths