from flask import jsonify, request

from services.prestamo_service import PrestamoService


class PrestamoController:
    def __init__(self, service: PrestamoService | None = None):
        self.service = service or PrestamoService()

    def listar(self):
        prestamos = self.service.listar_prestamos()
        return jsonify(
            {"success": True, "data": prestamos, "total": len(prestamos)}
        ), 200

    def listar_activos(self):
        prestamos = self.service.listar_activos()
        return jsonify(
            {"success": True, "data": prestamos, "total": len(prestamos)}
        ), 200

    def obtener(self, prestamo_id: int):
        prestamo = self.service.obtener_prestamo(prestamo_id)
        return jsonify({"success": True, "data": prestamo}), 200

    def crear(self):
        payload = request.get_json(silent=True)
        prestamo = self.service.crear_prestamo(payload)
        return jsonify(
            {"success": True, "data": prestamo, "message": "Préstamo registrado"}
        ), 201

    def devolver(self, prestamo_id: int):
        prestamo = self.service.devolver_prestamo(prestamo_id)
        return jsonify(
            {"success": True, "data": prestamo, "message": "Libro devuelto"}
        ), 200

    def estadisticas(self):
        stats = self.service.obtener_estadisticas()
        return jsonify({"success": True, "data": stats}), 200
