from flask import Blueprint, render_template, redirect, request, url_for, flash
from Backend.interface import PatientId, Interface, PatientData
from typing import Optional, Dict
from Backend.backend_interface import BackendManager
from Frontend.FlashMessageTypes import FlashMessageTypes
from datetime import date, datetime

import datetime

controller: Interface = BackendManager()

person_data = Blueprint("person_data", __name__)


@person_data.context_processor
def py_types() -> Dict[str, type]:
    """
    make some py-types accessible in the templates

    :return: types to use in the templates
    """
    return {
        "int": int,
        "bool": bool,
        "str": str,
        "float": float,
        "date": date
    }


@person_data.route("/")
def get_empty_patient_data():
    """
    generate empty patient data template

    :return: render the empty patient template
    """
    data = PatientData(birthdate=datetime.date.today(),
                        # Full name
                        name="",
                        hasCovid=False,
                        hasFever=False,
                        # Ausschlag auf der Haut
                        hasExanthem=False,
                        # Entzündung im Mundraum (Lippen, Zunge, Mundschleimhaut)
                        hasEnanthem=False,
                        # Geschwollene, gerötete Extremitäten
                        hasSwollenExtremeties=False,
                        # Bindehautentzündung
                        hasConjunctivitis=False,
                        # Geschwollene Lymphknoten
                        hasSwollenLymphnodes=False,
                        # Erbrechen, Übelkeit, Durchfall und/oder Bauchschmerzen
                        hasGastroIntestinalCondition=False,
                        # Aszites (Flüssigkeitsansammlung im Bauchraum)
                        hasAscites=False,
                        # Perikardergüsse (Flüssigkeitsansammlung im Herzbeutel)
                        hasPericardialEffusions=False,
                        # Pleuraergüsse (Flüssigkeitsansammlung in der Lunge)
                        hasPleuralEffusions=False,
                        # Perikarditits (Herzbeutelentzündung)
                        hasPericarditis=False,
                        # Hat Myokarditis (Herzmuskelenzündung)
                        hasMyocarditis=False
                        )
    return render_template("person_data.html", patient_data=data, annotations=PatientData.__annotations__)


@person_data.route("/<int:patient_id>")
def get_patient_data(patient_id: PatientId):
    """
    get data for the patient with the given id

    :param patient_id:
    :return: render template with patient data
    """
    return render_template("person_data.html",
                           pagename="Patientendaten",
                           patient_id=patient_id,
                           patient_data=controller.get_patient_data(patient_id),
                           annotations=PatientData.__annotations__)


def get_patient_data_from_request() -> Optional[PatientData]:
    """
    extract the patient data from the request

    :return: None or the PatientData
    """
    patient_data: PatientData = {}
    for key, data_type in PatientData.__annotations__.items():
        if key in request.form:
            if data_type is bool:
                patient_data[key] = True
            elif data_type is date:
                patient_data[key] = datetime.datetime.strptime(request.form[key], "%Y-%m-%d")
            else:
                patient_data[key] = request.form[key]

        elif key not in request.form and data_type is bool:
            patient_data[key] = False

        else:
            return None
    return patient_data


@person_data.route("/save", methods=['POST'])
def add_patient_data():
    """
    add a new patient
    """
    patient_data = get_patient_data_from_request()

    if patient_data is None:
        flash("Hinzufügen eines neuen Patienten ist fehlgeschlagen.", FlashMessageTypes.FAILURE.value)
        return redirect("/")

    patient_id = controller.add_patient(patient_data)

    if patient_id:
        flash(f"Patient {patient_data['name']} wurde erfolgreich hinzugefügt.", FlashMessageTypes.SUCCESS.value)
        return redirect(url_for('.get_patient_data', patient_id=patient_id))
    else:
        flash(f"Hinzufügen des Patienten  {patient_data['name']} ist fehlgeschlagen.", FlashMessageTypes.FAILURE.value)
        return redirect(url_for(".get_empty_patient_data"))


@person_data.route("/<int:patient_id>/save", methods=['POST'])
def update_patient_data(patient_id: PatientId):
    """
    update data of an existing patient
    """
    patient_data = get_patient_data_from_request()

    if patient_data is None:
        flash(f"Aktualisieren eines Patienten mit der ID:({patient_id}) schlug fehl.", FlashMessageTypes.FAILURE.value)
        return redirect(url_for(".get_patient_data", patient_id=patient_id))

    if controller.update_patient(patient_id, patient_data):
        flash(f"Patient {patient_data['name']} wurde erfolgreich aktualisiert.", FlashMessageTypes.SUCCESS.value)
        return redirect(url_for('.get_patient_data', patient_id=patient_id))
    else:
        flash(f"Aktualisieren eines Patienten (id: {patient_id}) {patient_data['name']} schlug fehl.", FlashMessageTypes.FAILURE.value)
        return redirect(url_for(".get_patient_data", patient_id=patient_id))
