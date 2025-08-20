from fastapi import FastAPI
from db.mysql_client_db import db_engine

app = FastAPI()

@app.get('/')
async def main():
        with db_engine.connect() as conn:
            return {'section': 'main'}