from flask import Blueprint

from controllers.prestamo_controller import PrestamoController

prestamos_bp = Blueprint("prestamos", __name__)
controller = PrestamoController()


@prestamos_bp.get("/prestamos")
def listar_prestamos():
    return controller.listar()


@prestamos_bp.get("/prestamos/activos")
def listar_activos():
    return controller.listar_activos()


@prestamos_bp.get("/prestamos/estadisticas")
def estadisticas_prestamos():
    return controller.estadisticas()


@prestamos_bp.get("/prestamos/<int:prestamo_id>")
def obtener_prestamo(prestamo_id: int):
    return controller.obtener(prestamo_id)


@prestamos_bp.post("/prestamos")
def crear_prestamo():
    return controller.crear()


@prestamos_bp.put("/prestamos/<int:prestamo_id>/devolver")
def devolver_prestamo(prestamo_id: int):
    return controller.devolver(prestamo_id)
