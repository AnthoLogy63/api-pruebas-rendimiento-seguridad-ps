import re
from datetime import datetime, timedelta
from typing import Any, Optional

from repositories.libro_repository import LibroRepository
from repositories.prestamo_repository import PrestamoRepository
from services.exceptions import ConflictError, NotFoundError, ValidationError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class PrestamoService:
    DEFAULT_DAYS = 14
    MAX_DAYS = 90

    def __init__(
        self,
        repository: Optional[PrestamoRepository] = None,
        libro_repository: Optional[LibroRepository] = None,
    ):
        self.repository = repository or PrestamoRepository()
        self.libro_repository = libro_repository or LibroRepository()

    def listar_prestamos(self) -> list[dict]:
        return [p.to_dict() for p in self.repository.find_all()]

    def listar_activos(self) -> list[dict]:
        return [p.to_dict() for p in self.repository.find_activos()]

    def obtener_prestamo(self, prestamo_id: int) -> dict:
        prestamo = self.repository.find_by_id(prestamo_id)
        if prestamo is None:
            raise NotFoundError(f"Préstamo con id {prestamo_id} no encontrado")
        return prestamo.to_dict()

    def crear_prestamo(self, payload: dict) -> dict:
        data = self._validate_payload(payload)
        libro = self.libro_repository.find_by_id(data["libro_id"])
        if libro is None:
            raise NotFoundError(f"Libro con id {data['libro_id']} no encontrado")
        if libro.cantidad_disponible <= 0:
            raise ConflictError(
                f"No hay ejemplares disponibles de '{libro.titulo}'"
            )

        try:
            prestamo = self.repository.create(data)
        except ValueError as exc:
            if str(exc) == "sin_stock":
                raise ConflictError(
                    f"No hay ejemplares disponibles de '{libro.titulo}'"
                )
            raise

        return prestamo.to_dict()

    def devolver_prestamo(self, prestamo_id: int) -> dict:
        prestamo = self.repository.find_by_id(prestamo_id)
        if prestamo is None:
            raise NotFoundError(f"Préstamo con id {prestamo_id} no encontrado")

        try:
            updated = self.repository.devolver(prestamo_id)
        except ValueError as exc:
            if str(exc) == "ya_devuelto":
                raise ConflictError("El préstamo ya fue devuelto")
            raise

        if updated is None:
            raise NotFoundError(f"Préstamo con id {prestamo_id} no encontrado")
        return updated.to_dict()

    def obtener_estadisticas(self) -> dict:
        return self.repository.get_estadisticas()

    def _validate_payload(self, payload: Any) -> dict:
        if not isinstance(payload, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser un objeto JSON")

        libro_id = payload.get("libro_id")
        if libro_id is None:
            raise ValidationError("El campo 'libro_id' es obligatorio")
        try:
            libro_id = int(libro_id)
        except (TypeError, ValueError):
            raise ValidationError("El campo 'libro_id' debe ser un número entero válido")
        if libro_id <= 0:
            raise ValidationError("El campo 'libro_id' debe ser mayor a 0")

        nombre = self._validate_required_string(payload.get("nombre_usuario"), "nombre_usuario")
        email = self._validate_email(payload.get("email"))

        dias = payload.get("dias_prestamo", self.DEFAULT_DAYS)
        try:
            dias = int(dias)
        except (TypeError, ValueError):
            raise ValidationError("El campo 'dias_prestamo' debe ser un número entero válido")
        if dias < 1 or dias > self.MAX_DAYS:
            raise ValidationError(
                f"El campo 'dias_prestamo' debe estar entre 1 y {self.MAX_DAYS}"
            )

        fecha_devolucion = (datetime.now() + timedelta(days=dias)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return {
            "libro_id": libro_id,
            "nombre_usuario": nombre,
            "email": email,
            "fecha_devolucion_esperada": fecha_devolucion,
        }

    def _validate_required_string(self, value: Any, field_name: str) -> str:
        if value is None:
            raise ValidationError(f"El campo '{field_name}' es obligatorio")
        text = str(value).strip()
        if not text:
            raise ValidationError(f"El campo '{field_name}' no puede estar vacío")
        return text

    def _validate_email(self, value: Any) -> str:
        if value is None:
            raise ValidationError("El campo 'email' es obligatorio")
        email = str(value).strip().lower()
        if not email or not EMAIL_PATTERN.match(email):
            raise ValidationError("El campo 'email' debe ser un correo válido")
        return email
