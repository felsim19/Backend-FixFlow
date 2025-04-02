from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import company, worker, bill, brands, devices, phone, delivery, outlow, shift, reparation
from connection.config import engine
from models.company import base
from models.worker import base
from models.shift import base
from models.devices import base
from models.brands import base
from models.phone import base
from models.bill import base
from models.delivery import base
from models.outflow import base
from models.reparation import base

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

base.metadata.create_all(bind=engine)

app.include_router(company.router)
app.include_router(worker.router)
app.include_router(shift.router)
app.include_router(delivery.router)
app.include_router(outlow.router)
app.include_router(bill.router)
app.include_router(brands.router)
app.include_router(devices.router)
app.include_router(phone.router)
app.include_router(reparation.router)


