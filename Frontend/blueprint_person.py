from flask import Blueprint, render_template, redirect, request, url_for, flash
from Backend.interface import PatientId, Interface, PatientData
from typing import Optional
from Backend.backend_interface import BackendManager
from Frontend.FlashMessageTypes import FlashMessageTypes

import datetime

controller: Interface = BackendManager()

person_data = Blueprint("person_data", __name__)


@person_data.context_processor
def py_types():
    return {
        "int": int,
        "bool": bool,
        "str": str,
        "float": float
    }


@person_data.route("/")
def get_empty_patient_data():
    birthdate = datetime.date.today()
    data = PatientData(birthdate=birthdate, name="Tom", hasCovid=False, hasFever=False)
    return render_template("person_data.html", patient_data=data, annotations=PatientData.__annotations__)


@person_data.route("/<int:patient_id>")
def get_patient_data(patient_id: PatientId):
    # ToDo: translate to german
    return render_template("person_data.html",
                           pagename="Patientendaten",
                           patient_id=patient_id,
                           patient_data=controller.get_patient_data(patient_id),
                           annotations=PatientData.__annotations__)


def get_patient_data_from_request() -> Optional[PatientData]:
    patient_data: PatientData = {}
    for key, data_type in PatientData.__annotations__.items():
        if key in request.form:
            if data_type is not bool:
                patient_data[key] = request.form[key]
            else:
                patient_data[key] = True
        elif key not in request.form and data_type is bool:
            patient_data[key] = False

        else:
            return None
    return patient_data


@person_data.route("/save", methods=['POST'])
def add_patient_data():
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
