from flask import Blueprint, redirect, render_template, request, url_for

from app.controllers.decorators import role_required, view_login_required, view_role_required
from app.models import Role
from app.services.patient_service import PatientService
from app.utils.responses import api_response

patients_bp = Blueprint("patients", __name__, url_prefix="")


@patients_bp.get("/patients")
@view_login_required
def list_patients_view():
    patients = PatientService.search(request.args.get("q"))
    return render_template("patients/index.html", patients=patients, q=request.args.get("q", ""))


@patients_bp.get("/patients/new")
@view_role_required(Role.RECEPCIONISTA.value)
def new_patient_view():
    return render_template("patients/form.html", patient=None)


@patients_bp.post("/patients")
@view_role_required(Role.RECEPCIONISTA.value)
def create_patient_view():
    PatientService.create(request.form)
    return redirect(url_for("patients.list_patients_view"))


@patients_bp.get("/patients/<int:patient_id>/edit")
@view_role_required(Role.RECEPCIONISTA.value)
def edit_patient_view(patient_id):
    return render_template("patients/form.html", patient=PatientService.get(patient_id))


@patients_bp.post("/patients/<int:patient_id>/edit")
@view_role_required(Role.RECEPCIONISTA.value)
def update_patient_view(patient_id):
    PatientService.update(patient_id, request.form)
    return redirect(url_for("patients.list_patients_view"))


@patients_bp.get("/api/patients")
@role_required(Role.RECEPCIONISTA.value, Role.MEDICO.value)
def search_patients_api():
    patients = PatientService.search(request.args.get("q"))
    return api_response(True, [patient.to_dict() for patient in patients])


@patients_bp.post("/api/patients")
@role_required(Role.RECEPCIONISTA.value)
def create_patient_api():
    patient = PatientService.create(request.get_json() or {})
    return api_response(True, patient.to_dict(), 201)


@patients_bp.put("/api/patients/<int:patient_id>")
@role_required(Role.RECEPCIONISTA.value)
def update_patient_api(patient_id):
    patient = PatientService.update(patient_id, request.get_json() or {})
    return api_response(True, patient.to_dict())
