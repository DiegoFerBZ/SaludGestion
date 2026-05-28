from flask import Blueprint, redirect, render_template, request, url_for

from app.controllers.decorators import current_view_user, role_required, view_login_required, view_role_required
from app.models import Role
from app.services.medical_record_service import MedicalRecordService
from app.services.patient_service import PatientService
from app.services.resource_service import ResourceService
from app.utils.responses import api_response

records_bp = Blueprint("records", __name__, url_prefix="")


@records_bp.get("/records")
@view_login_required
def list_records_view():
    patient_id = request.args.get("patient_id")
    records = MedicalRecordService.list_by_patient(patient_id) if patient_id else []
    return render_template("records/index.html", patients=PatientService.search(), records=records)


@records_bp.get("/records/new")
@view_role_required(Role.MEDICO.value)
def new_record_view():
    return render_template(
        "records/form.html",
        patients=PatientService.search(),
        doctors=ResourceService.list_doctors(),
        current_user=current_view_user(),
    )


@records_bp.post("/records")
@view_role_required(Role.MEDICO.value)
def create_record_view():
    MedicalRecordService.create(request.form)
    return redirect(url_for("records.list_records_view", patient_id=request.form.get("patient_id")))


@records_bp.post("/api/records")
@role_required(Role.MEDICO.value)
def create_record_api():
    record = MedicalRecordService.create(request.get_json() or {})
    return api_response(True, record.to_dict(), 201)


@records_bp.get("/api/patients/<int:patient_id>/records")
@role_required(Role.MEDICO.value, Role.RECEPCIONISTA.value)
def list_records_api(patient_id):
    records = MedicalRecordService.list_by_patient(patient_id)
    return api_response(True, [record.to_dict() for record in records])
