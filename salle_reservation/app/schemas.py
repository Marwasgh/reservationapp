from pydantic import BaseModel
from datetime import datetime

class ReservationCreate(BaseModel):
    salle_id: int
    debut: datetime
    fin: datetime

class ReservationOut(BaseModel):
    id: int
    user_id: int
    salle_id: int
    date_reservation: datetime
    debut: datetime
    fin: datetime

    class Config:
        from_attributes = True