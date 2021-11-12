from main import base
from sqlalchemy import Column, String, Integer


class Person(base):
    __tablename__ = 'person'
    __table_args__ = {"schema": "p21_cdm"}

    person_id = Column(Integer, primary_key=True)
    gender_concept_id = Column(Integer)
    year_of_birth = Column(Integer)
    month_of_birth = Column(Integer)
    day_of_birth = Column(Integer)
    race_concept_id = Column(Integer)
    ethnicity_concept_id = Column(Integer)
    location_id = Column(Integer)
    provider_id = Column(Integer)
    gender_source_value = Column(String(50))
    gender_source_concept_id = Column(Integer)
