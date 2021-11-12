from main import base
from sqlalchemy import Column, String, Integer


class Location(base):
    __tablename__ = 'location'
    __table_args__ = {"schema": "p21_cdm"}

    location_id = Column(Integer, primary_key=True)
    city = Column(String(50))
    zip = Column(String(9))
    location_source_value = Column(String(50))
