from sqlalchemy import Column, Integer, DateTime
from app.database import Base
from datetime import datetime

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  
    salle_id = Column(Integer, nullable=False)  
    date_reservation = Column(DateTime, default=datetime.utcnow)
    debut = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)