from sqlalchemy import Column, Integer, String
from app.database import Base

class Salle(Base):
    __tablename__ = 'salles'
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    capacite = Column(Integer)
    localisation = Column(String)
    etat = Column(String, default="disponible")