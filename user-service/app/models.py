from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

# Définition des rôles possibles avec Enum Python
class RoleEnum(PyEnum):
    admin = "admin"
    employe = "employe"
    visiteur = "visiteur"

# Modèle de table utilisateur
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  # Ajout du champ 'username'
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SqlEnum(RoleEnum), default=RoleEnum.visiteur, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"