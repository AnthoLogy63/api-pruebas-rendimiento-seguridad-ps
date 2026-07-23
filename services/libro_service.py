from datetime import datetime
from typing import Any, Optional

from repositories.libro_repository import LibroRepository
from repositories.prestamo_repository import PrestamoRepository
from services.exceptions import ConflictError, NotFoundError, ValidationError


class LibroService:
    MIN_YEAR = 1000
    MAX_YEAR = datetime.now().year + 1

    def __init__(
        self,
        repository: Optional[LibroRepository] = None,
        prestamo_repository: Optional[PrestamoRepository] = None,
    ):
        self.repository = repository or LibroRepository()
        self.prestamo_repository = prestamo_repository or PrestamoRepository()

    def listar_libros(self) -> list[dict]:
        return [libro.to_dict() for libro in self.repository.find_all()]

    def obtener_libro(self, libro_id: int) -> dict:
        libro = self.repository.find_by_id(libro_id)
        if libro is None:
            raise NotFoundError(f"Libro con id {libro_id} no encontrado")
        return libro.to_dict()

    def buscar_libros(
        self,
        titulo: Optional[str] = None,
        autor: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> list[dict]:
        libros = self.repository.search(
            titulo=titulo.strip() if titulo else None,
            autor=autor.strip() if autor else None,
            categoria=categoria.strip() if categoria else None,
        )
        return [libro.to_dict() for libro in libros]

    def crear_libro(self, payload: dict) -> dict:
        data = self._validate_payload(payload, is_update=False)
        existing = self.repository.find_by_isbn(data["isbn"])
        if existing is not None:
            raise ConflictError(f"Ya existe un libro con ISBN {data['isbn']}")
        libro = self.repository.create(data)
        return libro.to_dict()

    def actualizar_libro(self, libro_id: int, payload: dict) -> dict:
        existing = self.repository.find_by_id(libro_id)
        if existing is None:
            raise NotFoundError(f"Libro con id {libro_id} no encontrado")

        data = self._validate_payload(payload, is_update=True)
        isbn_owner = self.repository.find_by_isbn(data["isbn"])
        if isbn_owner is not None and isbn_owner.id != libro_id:
            raise ConflictError(f"Ya existe otro libro con ISBN {data['isbn']}")

        updated = self.repository.update(libro_id, data)
        if updated is None:
            raise NotFoundError(f"Libro con id {libro_id} no encontrado")
        return updated.to_dict()

    def eliminar_libro(self, libro_id: int) -> None:
        existing = self.repository.find_by_id(libro_id)
        if existing is None:
            raise NotFoundError(f"Libro con id {libro_id} no encontrado")

        activos = self.prestamo_repository.count_activos_by_libro(libro_id)
        if activos > 0:
            raise ConflictError(
                f"No se puede eliminar el libro: tiene {activos} préstamo(s) activo(s)"
            )

        historial = self.prestamo_repository.count_by_libro(libro_id)
        if historial > 0:
            raise ConflictError(
                f"No se puede eliminar el libro: tiene {historial} préstamo(s) en el historial"
            )

        deleted = self.repository.delete(libro_id)
        if not deleted:
            raise NotFoundError(f"Libro con id {libro_id} no encontrado")

    def listar_categorias(self) -> list[str]:
        return self.repository.get_categorias()

    def obtener_estadisticas(self) -> dict:
        return self.repository.get_estadisticas()

    def _validate_payload(self, payload: Any, is_update: bool) -> dict:
        if not isinstance(payload, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser un objeto JSON")

        titulo = self._validate_required_string(payload.get("titulo"), "titulo")
        autor = self._validate_required_string(payload.get("autor"), "autor")
        isbn = self._validate_required_string(payload.get("isbn"), "isbn")
        anio = self._validate_year(payload.get("anio_publicacion"))
        cantidad = self._validate_cantidad(payload.get("cantidad_disponible"))

        editorial = payload.get("editorial")
        if editorial is not None:
            editorial = str(editorial).strip() or None

        categoria = payload.get("categoria")
        if categoria is not None:
            categoria = str(categoria).strip() or None

        return {
            "titulo": titulo,
            "autor": autor,
            "isbn": isbn,
            "editorial": editorial,
            "anio_publicacion": anio,
            "categoria": categoria,
            "cantidad_disponible": cantidad,
        }

    def _validate_required_string(self, value: Any, field_name: str) -> str:
        if value is None:
            raise ValidationError(f"El campo '{field_name}' es obligatorio")
        text = str(value).strip()
        if not text:
            raise ValidationError(f"El campo '{field_name}' no puede estar vacío")
        return text

    def _validate_year(self, value: Any) -> int:
        if value is None:
            raise ValidationError("El campo 'anio_publicacion' es obligatorio")
        try:
            year = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                "El campo 'anio_publicacion' debe ser un número entero válido"
            )
        if year < self.MIN_YEAR or year > self.MAX_YEAR:
            raise ValidationError(
                f"El año de publicación debe estar entre {self.MIN_YEAR} y {self.MAX_YEAR}"
            )
        return year

    def _validate_cantidad(self, value: Any) -> int:
        if value is None:
            raise ValidationError("El campo 'cantidad_disponible' es obligatorio")
        try:
            cantidad = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                "El campo 'cantidad_disponible' debe ser un número entero válido"
            )
        if cantidad < 0:
            raise ValidationError(
                "El campo 'cantidad_disponible' debe ser mayor o igual a 0"
            )
        return cantidad
