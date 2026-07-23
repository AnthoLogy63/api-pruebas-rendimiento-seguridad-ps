from flask import jsonify, request

from services.libro_service import LibroService


class LibroController:
    def __init__(self, service: LibroService | None = None):
        self.service = service or LibroService()

    def listar(self):
        libros = self.service.listar_libros()
        return jsonify({"success": True, "data": libros, "total": len(libros)}), 200

    def obtener(self, libro_id: int):
        libro = self.service.obtener_libro(libro_id)
        return jsonify({"success": True, "data": libro}), 200

    def buscar(self):
        titulo = request.args.get("titulo")
        autor = request.args.get("autor")
        categoria = request.args.get("categoria")
        libros = self.service.buscar_libros(
            titulo=titulo, autor=autor, categoria=categoria
        )
        return jsonify({"success": True, "data": libros, "total": len(libros)}), 200

    def crear(self):
        payload = request.get_json(silent=True)
        libro = self.service.crear_libro(payload)
        return jsonify({"success": True, "data": libro, "message": "Libro creado"}), 201

    def actualizar(self, libro_id: int):
        payload = request.get_json(silent=True)
        libro = self.service.actualizar_libro(libro_id, payload)
        return jsonify(
            {"success": True, "data": libro, "message": "Libro actualizado"}
        ), 200

    def eliminar(self, libro_id: int):
        self.service.eliminar_libro(libro_id)
        return jsonify({"success": True, "message": "Libro eliminado"}), 200

    def categorias(self):
        categorias = self.service.listar_categorias()
        return jsonify(
            {"success": True, "data": categorias, "total": len(categorias)}
        ), 200

    def estadisticas(self):
        stats = self.service.obtener_estadisticas()
        return jsonify({"success": True, "data": stats}), 200

    def estado(self):
        return jsonify(
            {
                "success": True,
                "estado": "operativa",
                "biblioteca": "Biblioteca Nova",
                "mensaje": "Sistema de biblioteca en línea",
                "version": "2.0.0",
            }
        ), 200

    def health(self):
        """Alias técnico para herramientas de monitoreo (JMeter, K6)."""
        return self.estado()
