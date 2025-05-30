from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import company, worker, bill, brands, devices, phone, delivery, outlow, shift, reparation, premises, subcription, bold_webhook
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
from models.premises import base
from models.subscription import base

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tryventofixflow.vercel.app/", # frontend vercel
        "https://fixflow-tau.vercel.app", # frontend vercel
        "http://localhost:5173",  # Si pruebas localmente frontend
        "http://localhost:8000",  # Si pruebas localmente backend
        "https://fixflow.loca.lt", # url de local.lt    
        "https://backend-fixflow-production.up.railway.app/"  # url de railway
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
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
app.include_router(premises.router)
app.include_router(subcription.router)
app.include_router(bold_webhook.router)

