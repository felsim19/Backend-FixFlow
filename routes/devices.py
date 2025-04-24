from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.company import status
from schemas.devices import device, device_name as dn
from models.devices import devicesRegistration
from connection.config import get_db

router = APIRouter()

@router.post("/newDevice", response_model=status)
async def createDevice(device:device, db:Session=Depends(get_db)):
    new_device = devicesRegistration(
        id_brands=device.id_brands,
        name=device.name
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    return status(status="Marca registrada exitosamente")

@router.get("/allDevices")
async def get_Devices(db: Session = Depends(get_db)):
    try:
        Devices_list = db.query(devicesRegistration).all()  # Consulta sin filtro
        if not Devices_list:
            raise HTTPException(status_code=404, detail="No hay dispositvos registrados")
        return Devices_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{id_brands}/Devices")
async def get_Devices(id_brands:str,db: Session = Depends(get_db)):
    try:
        Devices_list = db.query(devicesRegistration).filter(devicesRegistration.id_brands == id_brands).all()  # Consulta sin filtro
        if not Devices_list:
            raise HTTPException(status_code=404, detail="No hay dispositvos registrados")
        return Devices_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/Devices/Edit/{id}", response_model=status)
async def updateDevice(id:int, device:dn, db:Session=Depends(get_db)):
    try:
        existing_device = db.query(devicesRegistration).filter(devicesRegistration.id == id).first()   

        if not existing_device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

        existing_device.name = device.name
        db.commit()
        db.refresh(existing_device)

        return status(status="Dispositivo actualizado exitosamente")
    except HTTPException:
        raise HTTPException(status_code=500, detail=str(e))
