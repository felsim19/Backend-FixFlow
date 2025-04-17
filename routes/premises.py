from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from connection.config import get_db
from models.premises import premisesRegistration
from models.VaultOut import outVaultRegistration
from models.company import companyRegistration
from schemas.Vault import vault
from models.shift import shiftRegistration
from schemas.company import status
from schemas.premises import (
    premises,
    somePremises as sp,
    loginPremises as lp,
    editPremises,
    somePremisesOutVault as svo,
)
import bcrypt

router = APIRouter()


@router.get("/premises/{company_id}/count")
async def get_worker_count(company_id: str, db: Session = Depends(get_db)):
    try:
        count = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.company == company_id)
            .count()
        )
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/premises/{selected_premises_id}")
async def get_company_color(selected_premises_id: int, db: Session = Depends(get_db)):
    try:
        premise = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == selected_premises_id)
            .first()
        )
        if not premise:
            raise HTTPException(status_code=404, detail="local no encontrado")
        return {"Vault": premise.vault}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/someDataOfPremises/{company}", response_model=list[sp])
async def someDataBill(company: str, db: Session = Depends(get_db)):
    try:
        query = text(
            """
            SELECT ref_premises, name, address, active
            FROM premises
            WHERE company = :company
        """
        )

        result = (
            db.execute(query, {"company": company}).mappings().all()
        )  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(status_code=404, detail="No hay locales registrados")

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/newPremises/{loggedCompany}/{premises_number}", response_model=status)
async def newPremises(
    loggedCompany: str,
    premises: premises,
    premises_number: int,
    db: Session = Depends(get_db),
):
    try:
        company = (
            db.query(companyRegistration)
            .filter(companyRegistration.company_user == loggedCompany)
            .first()
        )
        if not company:
            raise HTTPException(status_code=404, detail="Compañia no encontrada")

        if company.quantity_premises == premises_number:
            raise HTTPException(
                status_code=404, detail="No se puede crear mas sucursales"
            )

        encryption = bcrypt.hashpw(premises.password.encode("utf-8"), bcrypt.gensalt())

        new_premises = premisesRegistration(
            name=premises.name,
            address=premises.address,
            password=encryption.decode("utf-8"),
            company=loggedCompany,
        )
        new_premises.active = True
        db.add(new_premises)
        db.commit()
        db.refresh(new_premises)
        return status(status="Sucursal creada correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/someDataOutVault/{id}", response_model=list[svo])
async def someDataOutVault(id: int, db: Session = Depends(get_db)):
    try:

        query = text(
            """
            SELECT o.wname, o.date, o.quantity 
            FROM outvault as o 
            INNER JOIN shift as s ON o.ref_shift = s.ref_shift 
            INNER JOIN premises as p ON s.ref_premises = p.ref_premises 
            WHERE s.ref_premises = :id
            ORDER BY o.date DESC;       
        """
        )

        result = (
            db.execute(query, {"id": id}).mappings().all()
        )  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(
                status_code=404, detail="No hay dispositivos registrados"
            )

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searchWithdrawalsByWorker/{loggedid}/", response_model=list[svo])
async def someDataOutVault(id: int, db: Session = Depends(get_db)):
    try:

        query = text(
            """
            SELECT o.wname, o.date, o.quantity 
            FROM outvault as o 
            INNER JOIN shift as s ON o.ref_shift = s.ref_shift 
            INNER JOIN premises as p ON s.ref_premises = p.ref_premises 
            WHERE s.ref_premises = :id
            ORDER BY o.date DESC;       
        """
        )

        result = (
            db.execute(query, {"id": id}).mappings().all()
        )  # Aquí obtenemos las filas como diccionarios

        if not result:
            raise HTTPException(
                status_code=404, detail="No hay dispositivos registrados"
            )

        return result  # Ya no necesitas convertir manualmente

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/loginPremises", response_model=status)
async def loginPremises(login: lp, db: Session = Depends(get_db)):
    try:
        premises = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == login.premise_id)
            .first()
        )
        if not premises:
            raise HTTPException(status_code=404, detail="Local no encontrado")

        if not bcrypt.checkpw(
            login.password.encode("utf-8"), premises.password.encode("utf-8")
        ):
            raise HTTPException(status_code=404, detail="Contraseña incorrecta")

        if login.startShift:
            shift = (
                db.query(shiftRegistration)
                .filter(shiftRegistration.ref_shift == login.startShift)
                .first()
            )
            if not shift:
                raise HTTPException(status_code=404, detail="Turno no encontrado")

            if not shift.ref_premises:
                shift.ref_premises = premises.ref_premises
                db.commit()
                db.refresh(shift)

        return status(status="Login exitoso")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/OutFlowVault", response_model=status)
async def OutFlowVault(changes: vault, db: Session = Depends(get_db)):
    try:
        premise = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == changes.ref_premises)
            .first()
        )
        if not premise:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        if changes.quantity > premise.vault:
            raise HTTPException(
                status_code=401, detail="No hay suficiente dinero en caja"
            )
        premise.vault -= changes.quantity
        db.commit()
        db.refresh(premise)

        data = outVaultRegistration(
            ref_shift=changes.ref_shift, quantity=changes.quantity, wname=changes.wname
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        return status(status="Cambio de caja registrado correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/editPremises", response_model=status)
async def editPremises(changes: editPremises, db: Session = Depends(get_db)):
    try:
        premise = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == changes.ref_premises)
            .first()
        )
        if not premise:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        premise.name = changes.name
        premise.address = changes.address
        db.commit()
        db.refresh(premise)
        return status(status="Local editado correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/incativePremises/{ref_premises}", response_model=status)
async def incativePremises(ref_premises: int, db: Session = Depends(get_db)):
    try:
        premise = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == ref_premises)
            .first()
        )
        if not premise:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        premise.active = False
        db.commit()
        db.refresh(premise)
        return status(status="Local desactivado correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/activePremises/{ref_premises}", response_model=status)
async def activePremises(ref_premises: int, db: Session = Depends(get_db)):
    try:
        premise = (
            db.query(premisesRegistration)
            .filter(premisesRegistration.ref_premises == ref_premises)
            .first()
        )
        if not premise:
            raise HTTPException(status_code=404, detail="Local no encontrado")
        premise.active = True
        db.commit()
        db.refresh(premise)
        return status(status="Local activado correctamente")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
