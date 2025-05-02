import httpx
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app import models, schemas, database
from datetime import datetime, timedelta
from app.kafka_producer import envoyer_evenement

router = APIRouter()

# Vérifier l'existence de la salle via l'API
async def verifier_salle_existe(salle_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://salle_service:8001/salles/{salle_id}')
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Salle non trouvée")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service des salles indisponible")

# Récupérer l'utilisateur courant via auth_service
async def get_current_user(authorization: str = Header(...)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://auth_service:8000/profile",
                headers={"Authorization": authorization}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Token invalide")
            else:
                raise HTTPException(status_code=500, detail="Erreur du service d'authentification")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service d'authentification indisponible")

# Route pour créer une réservation
@router.post("/reservations/", response_model=schemas.ReservationOut)
async def reserver_salle(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    # Vérifier que la salle existe
    await verifier_salle_existe(reservation.salle_id)

    # Vérifier les conflits de réservation
    conflit = db.query(models.Reservation).filter(
        models.Reservation.salle_id == reservation.salle_id,
        models.Reservation.debut < reservation.fin,
        models.Reservation.fin > reservation.debut
    ).first()

    if conflit:
        raise HTTPException(status_code=409, detail="Salle déjà réservée pour ce créneau")

    # Créer la réservation
    nouvelle_reservation = models.Reservation(
        user_id=current_user["id"],  
        salle_id=reservation.salle_id,
        debut=reservation.debut,
        fin=reservation.fin
    )

    db.add(nouvelle_reservation)
    db.commit()
    db.refresh(nouvelle_reservation)

    envoyer_evenement("reservation.created", {
        "reservation_id": nouvelle_reservation.id,
        "user_id": current_user["id"],
        "salle_id": reservation.salle_id,
        "debut": str(reservation.debut),
        "fin": str(reservation.fin)
    })


    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://salle_service:8001/salles/{reservation.salle_id}/etat",
                json={"etat": "reservee"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Échec de la mise à jour de l'état de la salle")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service des salles indisponible pour mise à jour")


    return nouvelle_reservation

# Route pour lister les réservations
@router.get("/reservations/", response_model=list[schemas.ReservationOut])
def lister_reservations(db: Session = Depends(database.get_db)):
    return db.query(models.Reservation).all()


@router.get("/mes_reservations/", response_model=list[schemas.ReservationOut])
async def lister_mes_reservations(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    reservations = db.query(models.Reservation).filter(
        models.Reservation.user_id == current_user["id"]
    ).all()
    return reservations



@router.delete("/reservations/{reservation_id}", status_code=204)
async def annuler_reservation(
    reservation_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id,
        models.Reservation.user_id == current_user["id"]
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    # Vérifier la condition des 24 heures
    maintenant = datetime.utcnow()
    if reservation.debut - maintenant < timedelta(hours=24):
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez annuler une réservation que 24 heures à l'avance"
        )

    salle_id = reservation.salle_id
    db.delete(reservation)
    db.commit()

    envoyer_evenement("reservation.cancelled", {
        "reservation_id": reservation.id,
        "user_id": current_user["id"],
        "salle_id": salle_id
    })

    # Réinitialiser l'état de la salle
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://salle_service:8001/salles/{salle_id}/etat",
                json={"etat": "disponible"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Échec de mise à jour de l'état de la salle")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service des salles indisponible pour mise à jour")

    return {"detail": "Réservation annulée et salle libérée"}