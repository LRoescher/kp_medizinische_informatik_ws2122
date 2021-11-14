import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

username = 'noah2' # DB-Username
password = 'passwort' # DB-Password
url = 'localhost' # DB-URL
port = '5432' # DB-Port
name = 'OHDSI' # DB-Name

base = declarative_base()
db = create_engine('postgresql+psycopg2://'+username+':'+password+'@'+url+':'+port+'/'+name)
Session = sessionmaker(db)
session = Session()


def etl_process():
    case_df = pd.read_csv(
        '/Users/noah/kp_medizinische_informatik_ws2122/data/1. Bereistellung Daten/CASE.csv', sep=';')
    diagnosis_df = pd.read_csv(
        '/Users/noah/kp_medizinische_informatik_ws2122/data/1. Bereistellung Daten/DIAGNOSIS.csv', sep=';')
    lab_df = pd.read_csv(
        '/Users/noah/kp_medizinische_informatik_ws2122/data/1. Bereistellung Daten/LAB.csv', sep=';')
    person_df = pd.read_csv(
        '/Users/noah/kp_medizinische_informatik_ws2122/data/1. Bereistellung Daten/PERSON.csv', sep=';')
    procedure_df = pd.read_csv(
        '/Users/noah/kp_medizinische_informatik_ws2122/data/1. Bereistellung Daten/PROCEDURE.csv', sep=';')

    person_df = update_location(person_df)
    update_person(person_df)

def update_location(data):
    import location
    data['LOCATION_SOURCE_VALUE']=data.apply(lambda x:'City:%s ZIP:%s' % (x['CITY'],x['ZIP']),axis=1)
    for index, row in data.iterrows():
        new_entry = location.Location(location_id = index + 1,
                                      city = row['CITY'],
                                      zip = row['ZIP'],
                                      location_source_value = row['LOCATION_SOURCE_VALUE'])
        session.merge(new_entry)
        data.at[index,'LOCATION_ID'] = index + 1
    session.commit()
    return data

def update_person(data):
    import person
    data['BIRTHDATE'] = pd.to_datetime(data['BIRTHDATE'], format='%Y-%m-%d')
    data['YEAR'] = data['BIRTHDATE'].dt.year
    data['MONTH'] = data['BIRTHDATE'].dt.month
    data['DAY'] = data['BIRTHDATE'].dt.day
    data['GENDER_ID'] = [8532 if g == 'w' else 8507 if g == 'm' else 0 for g in data['GENDER']]
    data.drop(data[data['GENDER_ID'] == 0].index, inplace=True)

    for index, row in data.iterrows():
        new_entry = person.Person(person_id=row['PATIENT_ID'],
                                  gender_concept_id=row['GENDER_ID'],
                                  year_of_birth=row['YEAR'],
                                  month_of_birth=row['MONTH'],
                                  day_of_birth=row['DAY'],
                                  race_concept_id=4218674,
                                  ethnicity_concept_id=0,
                                  location_id=row['LOCATION_ID'],
                                  provider_id=row['PROVIDER_ID'],
                                  gender_source_value=row['GENDER'],
                                  gender_source_concept_id=None)
        session.merge(new_entry)
    session.commit()


if __name__ == '__main__':
    etl_process()
