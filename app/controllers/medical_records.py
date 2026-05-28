from flask import Blueprint, redirect, render_template, request, url_for

from app.controllers.decorators import current_view_user, role_required, view_login_required, view_role_required
from app.models import Role
from app.services.medical_record_service import MedicalRecordService
from app.utils.responses import api_response

records_bp = Blueprint("records", __name__, url_prefix="")


@records_bp.get("/records")
@view_login_required
def list_records_view():
    patient_document = request.args.get("patient_document")
    records = MedicalRecordService.list_by_patient_document(patient_document) if patient_document else []
    return render_template("records/index.html", records=records, patient_document=patient_document or "")


@records_bp.get("/records/new")
@view_role_required(Role.MEDICO.value)
def new_record_view():
    return render_template(
        "records/form.html",
        current_user=current_view_user(),
    )


@records_bp.post("/records")
@view_role_required(Role.MEDICO.value)
def create_record_view():
    MedicalRecordService.create_for_doctor(request.form, current_view_user().id)
    return redirect(url_for("records.list_records_view", patient_document=request.form.get("patient_document")))


@records_bp.post("/api/records")
@role_required(Role.MEDICO.value)
def create_record_api():
    from flask_jwt_extended import get_jwt_identity

    record = MedicalRecordService.create_for_doctor(request.get_json() or {}, get_jwt_identity())
    return api_response(True, record.to_dict(), 201)


@records_bp.get("/api/patients/<int:patient_id>/records")
@role_required(Role.MEDICO.value, Role.RECEPCIONISTA.value)
def list_records_api(patient_id):
    records = MedicalRecordService.list_by_patient(patient_id)
    return api_response(True, [record.to_dict() for record in records])
