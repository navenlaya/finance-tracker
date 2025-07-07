from fastapi import FastAPI
from app.api import api_router
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api_router)
