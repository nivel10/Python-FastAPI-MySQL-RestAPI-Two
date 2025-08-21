from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Query
from sqlmodel import select
from models.hero import Hero, HeroCreate, HeroPublic, HeroUpdate
from db.mysql_client_db import create_db_and_tables, session_dep


app = FastAPI()

#region API - paths
@app.get('/', tags=['main'])
async def main():
        # with db_engine.connect() as conn:
     return {'section': 'main'}
        
@app.on_event('startup')
async def on_startup():
    try:
        create_db_and_tables()
    except Exception as ex:
        print(str(ex))

@app.get('/heroes/', tags=['heroes'], response_model=list[HeroPublic])
async def get_hero(
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

@app.get('/heroes/{id}', tags=['heroes'], response_model=HeroPublic)
async def get_hero(id: int, session: session_dep):
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

@app.patch('/heroes/{id}', tags=['heroes'], response_model=HeroPublic)
async def update_hero(id: int, hero: HeroUpdate, session: session_dep,):
     try:
          hero_found = await get_hero(id=id, session=session)

          hero_updated = hero.model_dump(exclude_unset=True)
          hero_found.sqlmodel_update(hero_updated)
          session.add(hero_found)
          session.commit()
          session.refresh(hero_found)

          return hero_found
     except Exception as ex:
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=str(ex)
          )

@app.delete('/heroes/{id}', tags=['heroes'], response_model=HeroPublic)
async def delete_hero(id: int, session: session_dep):
     try:
          hero_found = await get_hero(id=id, session=session)

          session.delete(hero_found)
          session.commit()
          return hero_found
     except Exception as ex:
          raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=str(ex),
          )
#endregion API - paths