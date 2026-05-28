from flask import Blueprint, redirect, render_template, request, url_for

from app.controllers.decorators import role_required, view_role_required
from app.models import Role
from app.services.resource_service import ResourceService
from app.utils.responses import api_response

resources_bp = Blueprint("resources", __name__, url_prefix="")


@resources_bp.get("/resources")
@view_role_required(Role.RECEPCIONISTA.value)
def resources_view():
    return render_template(
        "resources/index.html",
        doctors=ResourceService.list_doctors(),
        rooms=ResourceService.list_rooms(),
    )


@resources_bp.post("/rooms")
@view_role_required(Role.RECEPCIONISTA.value)
def create_room_view():
    ResourceService.create_room(request.form)
    return redirect(url_for("resources.resources_view"))


@resources_bp.post("/doctors")
@view_role_required(Role.RECEPCIONISTA.value)
def create_doctor_view():
    ResourceService.create_doctor(request.form)
    return redirect(url_for("resources.resources_view"))


@resources_bp.post("/doctors/<int:doctor_id>/room")
@view_role_required(Role.RECEPCIONISTA.value)
def assign_room_view(doctor_id):
    ResourceService.assign_room(doctor_id, request.form.get("room_id"))
    return redirect(url_for("resources.resources_view"))


@resources_bp.get("/api/doctors")
@role_required(Role.RECEPCIONISTA.value)
def list_doctors_api():
    return api_response(True, [doctor.to_dict() for doctor in ResourceService.list_doctors()])


@resources_bp.post("/api/doctors")
@role_required(Role.RECEPCIONISTA.value)
def create_doctor_api():
    doctor = ResourceService.create_doctor(request.get_json() or {})
    return api_response(True, doctor.to_dict(), 201)


@resources_bp.get("/api/rooms")
@role_required(Role.RECEPCIONISTA.value)
def list_rooms_api():
    return api_response(True, [room.to_dict() for room in ResourceService.list_rooms()])


@resources_bp.post("/api/rooms")
@role_required(Role.RECEPCIONISTA.value)
def create_room_api():
    room = ResourceService.create_room(request.get_json() or {})
    return api_response(True, room.to_dict(), 201)
