from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import company, worker
from connection.config import engine
from models.company import base
from models.worker import base
from models.shift import base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

base.metadata.create_all(bind=engine)

app.include_router(company.router)
app.include_router(worker.router)

app.mount("/static", StaticFiles(directory="companyImg"), name="static")