from flask import Blueprint, render_template
from Backend.interface import PatientId, Interface
from Backend.patient_interface import Results

controller: Interface = Results()

results = Blueprint("results", __name__)

# ToDO: generate PDF


@results.route("/all")
def get_analysis():
    return render_template("analysis.html", analysis_data=controller.analysis_data)


@results.route("/pims/<int:patient_id>")
def result_pims(patient_id: PatientId):
    #ToDo: implement
    pass


@results.route("/kawasaki/<int:patient_id>")
def result_kawasaki(patient_id: int):
    #ToDo: implement
    pass