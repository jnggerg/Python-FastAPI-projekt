from fastapi import FastAPI
from .utvonalak import api

app = FastAPI()

app.include_router(api, tags=["Kurzusok"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"uzenet": "Üdvözöllek a Szakácsképző Intézmény FastAPI alkalmazásában!"}

