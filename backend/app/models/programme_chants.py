from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class ProgrammeChants(Base):
    __tablename__ = 'programme_chants'

    id = Column(Integer, primary_key=True, index=True)
    programme_culte_id = Column(Integer, ForeignKey("programme_culte.id"), nullable=False)
    chant_id = Column(Integer, ForeignKey("chants.id"), nullable=False)
    ordre = Column(Integer, nullable=False)

