from flask import Blueprint, render_template
from Backend.interface import PatientId, Interface, DecisionReasons, Disease
from Backend.example_interface import Example

controller: Interface = Example()

results = Blueprint("results", __name__)

# ToDO: generate PDF


@results.route("/all")
def get_analysis():
    return render_template("analysis.html", analysis_data=controller.analysis_data)


@results.route("/pims/<int:patient_id>")
def result_pims(patient_id: PatientId):
    return render_template("result.html",
                           patient_id=patient_id,
                           patient_data=controller.get_decision_reason(patient_id, Disease.PIMS),
                           annotations=DecisionReasons.__annotations__)


@results.route("/kawasaki/<int:patient_id>")
def result_kawasaki(patient_id: PatientId):
    return render_template("result.html",
                           patient_id=patient_id,
                           patient_data=controller.get_decision_reason(patient_id, Disease.KAWASAKI),
                           annotations=DecisionReasons.__annotations__)