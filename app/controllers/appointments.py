from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from app.controllers.decorators import role_required, view_login_required
from app.models import Role
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.resource_service import ResourceService
from app.utils.responses import api_response

appointments_bp = Blueprint("appointments", __name__, url_prefix="")


@appointments_bp.get("/appointments")
@view_login_required
def list_appointments_view():
    appointments = AppointmentService.list(
        doctor_id=request.args.get("doctor_id") or None,
        patient_id=request.args.get("patient_id") or None,
    )
    return render_template(
        "appointments/index.html",
        appointments=appointments,
        doctors=ResourceService.list_doctors(),
    )


@appointments_bp.get("/appointments/new")
@view_login_required
def new_appointment_view():
    return render_template(
        "appointments/form.html",
        patients=PatientService.search(),
        doctors=ResourceService.list_doctors(),
    )


@appointments_bp.post("/appointments")
@view_login_required
def create_appointment_view():
    AppointmentService.create(request.form)
    return redirect(url_for("appointments.list_appointments_view"))


@appointments_bp.post("/appointments/<int:appointment_id>/cancel")
@view_login_required
def cancel_appointment_view(appointment_id):
    AppointmentService.cancel(appointment_id, request.form.get("reason"))
    return redirect(url_for("appointments.list_appointments_view"))


@appointments_bp.get("/availability")
@view_login_required
def availability_view():
    doctors = ResourceService.list_doctors()
    selected_doctor = request.args.get("doctor_id") or (doctors[0].id if doctors else None)
    selected_date = request.args.get("date") or date.today().isoformat()
    availability = None
    if selected_doctor:
        availability = AppointmentService.availability(int(selected_doctor), selected_date)
    return render_template(
        "appointments/availability.html",
        doctors=doctors,
        selected_doctor=int(selected_doctor) if selected_doctor else None,
        selected_date=selected_date,
        availability=availability,
    )


@appointments_bp.get("/api/appointments")
@role_required(Role.RECEPCIONISTA.value, Role.MEDICO.value)
def list_appointments_api():
    appointments = AppointmentService.list(request.args.get("doctor_id"), request.args.get("patient_id"))
    return api_response(True, [appointment.to_dict() for appointment in appointments])


@appointments_bp.post("/api/appointments")
@role_required(Role.RECEPCIONISTA.value)
def create_appointment_api():
    appointment = AppointmentService.create(request.get_json() or {})
    return api_response(True, appointment.to_dict(), 201)


@appointments_bp.post("/api/appointments/<int:appointment_id>/cancel")
@role_required(Role.RECEPCIONISTA.value, Role.MEDICO.value)
def cancel_appointment_api(appointment_id):
    appointment = AppointmentService.cancel(appointment_id, (request.get_json() or {}).get("reason"))
    return api_response(True, appointment.to_dict())


@appointments_bp.get("/api/doctors/<int:doctor_id>/availability")
@role_required(Role.RECEPCIONISTA.value, Role.MEDICO.value)
def availability_api(doctor_id):
    return api_response(True, AppointmentService.availability(doctor_id, request.args.get("date")))
