from flask import Blueprint

from controllers.libro_controller import LibroController

libros_bp = Blueprint("libros", __name__)
controller = LibroController()


@libros_bp.get("/biblioteca/estado")
def estado_biblioteca():
    return controller.estado()


@libros_bp.get("/health")
def health():
    return controller.health()


@libros_bp.get("/libros")
def listar_libros():
    return controller.listar()


@libros_bp.get("/libros/buscar")
def buscar_libros():
    return controller.buscar()


@libros_bp.get("/libros/categorias")
def listar_categorias():
    return controller.categorias()


@libros_bp.get("/libros/estadisticas")
def obtener_estadisticas():
    return controller.estadisticas()


@libros_bp.get("/libros/<int:libro_id>")
def obtener_libro(libro_id: int):
    return controller.obtener(libro_id)


@libros_bp.post("/libros")
def crear_libro():
    return controller.crear()


@libros_bp.put("/libros/<int:libro_id>")
def actualizar_libro(libro_id: int):
    return controller.actualizar(libro_id)


@libros_bp.delete("/libros/<int:libro_id>")
def eliminar_libro(libro_id: int):
    return controller.eliminar(libro_id)
