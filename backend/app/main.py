from fastapi import FastAPI
from app.api import api_router
from app.db.session import Base, engine
from app.models import user, plaid  

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(api_router)
