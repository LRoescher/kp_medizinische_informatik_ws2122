from flask import Blueprint, render_template
from Backend.backend_interface import BackendManager
from Backend.interface import PatientId, Interface, DecisionReasons, Disease, PatientData

controller: Interface = BackendManager()

results = Blueprint("results", __name__)

# ToDO: generate PDF


@results.route("/all")
def get_analysis():
    """
    render analysis template
    """
    return render_template("analysis.html", pagename="Analyse", analysis_data=controller.analysis_data)


@results.route("/pims/<int:patient_id>")
def result_pims(patient_id: PatientId):
    """
    render the result template for the given patient and pims
    """
    return render_template("result.html",
                           pagename="Pims",
                           patient_id=patient_id,
                           decision_reason_data=controller.get_decision_reason(patient_id, Disease.PIMS),
                           decision_reason_annotations=DecisionReasons.__annotations__,
                           patient_data=controller.get_patient_data(patient_id),
                           annotations=PatientData.__annotations__)


@results.route("/kawasaki/<int:patient_id>")
def result_kawasaki(patient_id: PatientId):
    """
    render the result template for the given patient and kawasaki
    """
    return render_template("result.html",
                           pagename="Kawasaki",
                           patient_id=patient_id,
                           decision_reason_data=controller.get_decision_reason(patient_id, Disease.KAWASAKI),
                           decision_reason_annotations=DecisionReasons.__annotations__,
                           patient_data=controller.get_patient_data(patient_id),
                           annotations=PatientData.__annotations__)
