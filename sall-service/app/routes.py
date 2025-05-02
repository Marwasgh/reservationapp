from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models, schemas, database

router = APIRouter(
    prefix="/salles",
    tags=["Salles"]
)

# Dépendance pour obtenir la session de la base de données
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.SalleResponse, status_code=status.HTTP_201_CREATED)
def create_salle(salle: schemas.SalleCreate, db: Session = Depends(get_db)):
    db_salle = models.Salle(nom=salle.nom, capacite=salle.capacite, localisation=salle.localisation)
    db.add(db_salle)
    db.commit()
    db.refresh(db_salle)
    return db_salle

@router.get("/", response_model=list[schemas.SalleResponse])
def get_salles(db: Session = Depends(get_db)):
    return db.query(models.Salle).all()

@router.get("/{salle_id}", response_model=schemas.SalleResponse)
def get_salle(salle_id: int, db: Session = Depends(get_db)):
    salle = db.query(models.Salle).filter(models.Salle.id == salle_id).first()
    if salle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")
    return salle

@router.put("/{salle_id}", response_model=schemas.SalleResponse)
def update_salle(salle_id: int, salle: schemas.SalleCreate, db: Session = Depends(get_db)):
    db_salle = db.query(models.Salle).filter(models.Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")

    db_salle.nom = salle.nom
    db_salle.capacite = salle.capacite
    db_salle.localisation = salle.localisation
    db.commit()
    db.refresh(db_salle)
    return db_salle

@router.delete("/{salle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salle(salle_id: int, db: Session = Depends(get_db)):
    db_salle = db.query(models.Salle).filter(models.Salle.id == salle_id).first()
    if db_salle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")

    db.delete(db_salle)
    db.commit()
    return {"detail": "Salle supprimée"}


@router.patch("/{salle_id}/etat")
def modifier_etat_salle(salle_id: int, etat: dict, db: Session = Depends(get_db)):
    salle = db.query(models.Salle).get(salle_id)
    if not salle:
        raise HTTPException(status_code=404, detail="Salle non trouvée")
    salle.etat = etat["etat"]
    db.commit()
    db.refresh(salle)
    return salle