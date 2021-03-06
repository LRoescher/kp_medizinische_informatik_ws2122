from flask import Blueprint, send_file, request, flash, redirect, render_template, url_for, jsonify
from Frontend.FlashMessageTypes import FlashMessageTypes
from Backend.interface import Interface
from Backend.backend_interface import BackendManager
from typing import Dict, Optional
from config.definitions import ROOT_DIR
import os

# Data files
CASE = "CASE.csv"
DIAGNOSIS = "DIAGNOSIS.csv"
LAB = "LAB.csv"
PERSON = "PERSON.csv"
PROCEDURE = "PROCEDURE.csv"

data_manager = Blueprint("data_manager", __name__)
upload_folder = os.path.join(ROOT_DIR, "upload")

config_path = os.path.join(ROOT_DIR, "config", "config.yml")
case_path = os.path.join(upload_folder, CASE)
diagnosis_path = os.path.join(upload_folder, DIAGNOSIS)
lab_path = os.path.join(upload_folder, LAB)
person_path = os.path.join(upload_folder, PERSON)
procedure_path = os.path.join(upload_folder, PROCEDURE)

case_head = ["CASE_ID", "PROVIDER_ID", "PATIENT_ID", "START_DATE", "END_DATE"]
diagnosis_head = ["PROVIDER_ID", "PATIENT_ID", "ADMISSION_NUMBER", "ADMISSION_DATE", "CLINICAL_STATUS", "ORPHA_CODE",
                  "ORPHA_TEXT", "ALPHAID_CODE", "ALPHAID_TEXT", "ICD_PRIMARY_CODE", "ICD_TEXT", "ICD_SECONDARY_CODE",
                  "DIAGNOSTIC_EXPLANATION", "ICD_VERSION", "ICD_MANIFESTATION", "DIAGNOSIS_TYPE"]
lab_head = ["IDENTIFIER", "STATUS", "CATEGORY", "PARAMETER_NAME", "PARAMETER_LOINC", "Patientidentifikator",
            "TEST_DATE", "NUMERIC_VALUE", "TEXTUAL_VALUE", "UNIT", "NORMAL_VALUES", "IS_NORMAL", "DEVIATION",
            "COMMENT", "UCUM_UNIT"]
lab_head_alt = ["IDENTIFIER", "STATUS", "CATEGORY", "PARAMETER_NAME", "PARAMETER_LOINC", "PATIENT_ID",
                "TEST_DATE", "NUMERIC_VALUE", "TEXTUAL_VALUE", "UNIT", "NORMAL_VALUES", "IS_NORMAL", "DEVIATION",
                "COMMENT", "UCUM_UNIT"]
person_head = ["PROVIDER_ID", "PATIENT_ID", "NAME", "FORNAME", "GENDER", "BIRTHDATE", "CITY", "ZIP", "DEATH",
               "DEATH_DATE", "DATE_OF_LIFE", "INSURANCE", "INSURANCE_ID"]
procedure_head = ["ID", "OPS_VERSION", "OPS_CODE", "PATIENT_ID", "EXECUTION_DATE"]

controller: Interface = BackendManager()


def check_existing_files() -> Dict[str, bool]:
    """
    check if all needed files are there

    :return: dict with name of the file followed by true if the file exists
    """
    if not os.path.isdir(upload_folder):
        os.mkdir(path=upload_folder)
    return {
        "config": True if os.path.isfile(config_path) else False,
        "case": True if os.path.isfile(case_path) else False,
        "diagnosis": True if os.path.isfile(diagnosis_path) else False,
        "lab": True if os.path.isfile(lab_path) else False,
        "person": True if os.path.isfile(person_path) else False,
        "procedure": True if os.path.isfile(procedure_path) else False,
    }


def clear_uploads() -> bool:
    """
    remove the csv files from the upload directory

    :return: true
    """
    print("clear data")
    for file in [case_path, diagnosis_path, lab_path, person_path, procedure_path]:
        if os.path.isfile(file):
            os.remove(file)
    return True


@data_manager.route("/etl")
def upload_page():
    """
    render the load_batch template
    """
    ex_f = check_existing_files()
    config_exists = ex_f["config"]
    del ex_f["config"]
    data_exists = all(ex_f.values())
    return render_template("load_batch.html",
                           paggename="Datensatz hinzuf??gen",
                           config_exists=config_exists,
                           data_exists=data_exists)


@data_manager.route("/etl/run", methods=["POST"])
def run_etl():
    """
    run the etl job
    """
    controller.reset_config()
    success = controller.run_etl(upload_folder)
    return jsonify({"success": success})


@data_manager.route('/etl/upload', methods=['POST'])
def upload_file():
    """
    handle files that are uploaded

    :return: success - the csv is correct; complete - all csvs are uploaded
    """
    success: bool = True
    complete: bool = True
    msg: str = ""

    try:
        key: str = request.form["key"]
        file = request.files["file"]
        path: Optional[str] = None
        check_list = None

        print(request.form)
        if request.form["uploads"] == '1':
            clear_uploads()
        print("data cleared")

        if key == "config":
            path = config_path
        elif key == "case":
            path = case_path
            check_list = case_head
        elif key == "diagnosis":
            path = diagnosis_path
            check_list = diagnosis_head
        elif key == "lab":
            path = lab_path
            check_list = lab_head
        elif key == "person":
            path = person_path
            check_list = person_head
        elif key == "procedure":
            path = procedure_path
            check_list = procedure_head

        file.save(path)

        if check_list is not None:
            with open(path) as f:
                actual_head = f.readline().strip().replace(" ", "").split(";")
                if set(check_list) != set(actual_head):
                    if key != 'lab' or set(lab_head_alt) != set(actual_head):
                        success = False
                        os.remove(path)
        print("check", success)

        complete = all(check_existing_files().values())

    except Exception as e:
        success = complete = False
        print(e)

    return jsonify({"success": success, "complete": complete})


@data_manager.route("/config")
def download_config():
    """
    download the config file
    """
    return send_file(config_path, as_attachment=True)


@data_manager.route("/reset_db")
def reset_db():
    """
    reset the database
    """
    if controller.reset_db():
        flash("Datenbank erfolgreich zur??ckgesetzt.", FlashMessageTypes.SUCCESS.value)
    else:
        flash("Datenbank konnte nicht zur??ckgesetzt werden.", FlashMessageTypes.FAILURE.value)
    return redirect(url_for("settings"))


@data_manager.route("/analysis/run", methods=['POST', 'GET'])
def analyse_data():
    """
    start the process which analyses the data in the db
    """
    success = controller.run_analysis()
    if request.method == 'POST':
        return jsonify({"success": success})
    else:
        if success:
            flash("Daten wurden erfolgreich analysiert.", FlashMessageTypes.SUCCESS.value)
        else:
            flash("Analyse der Daten ist fehlgeschlagen.", FlashMessageTypes.FAILURE.value)
        return redirect(url_for("settings"))
