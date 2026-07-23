from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Prestamo:
    id: Optional[int]
    libro_id: int
    nombre_usuario: str
    email: str
    fecha_prestamo: str
    fecha_devolucion_esperada: str
    fecha_devolucion_real: Optional[str]
    estado: str
    created_at: Optional[str] = None
    libro_titulo: Optional[str] = None
    libro_autor: Optional[str] = None

    @classmethod
    def from_row(cls, row: Any) -> "Prestamo":
        return cls(
            id=row["id"],
            libro_id=row["libro_id"],
            nombre_usuario=row["nombre_usuario"],
            email=row["email"],
            fecha_prestamo=row["fecha_prestamo"],
            fecha_devolucion_esperada=row["fecha_devolucion_esperada"],
            fecha_devolucion_real=row["fecha_devolucion_real"],
            estado=row["estado"],
            created_at=row["created_at"],
            libro_titulo=row["libro_titulo"] if "libro_titulo" in row.keys() else None,
            libro_autor=row["libro_autor"] if "libro_autor" in row.keys() else None,
        )

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "libro_id": self.libro_id,
            "nombre_usuario": self.nombre_usuario,
            "email": self.email,
            "fecha_prestamo": self.fecha_prestamo,
            "fecha_devolucion_esperada": self.fecha_devolucion_esperada,
            "fecha_devolucion_real": self.fecha_devolucion_real,
            "estado": self.estado,
            "created_at": self.created_at,
        }
        if self.libro_titulo is not None:
            data["libro_titulo"] = self.libro_titulo
        if self.libro_autor is not None:
            data["libro_autor"] = self.libro_autor
        return data
