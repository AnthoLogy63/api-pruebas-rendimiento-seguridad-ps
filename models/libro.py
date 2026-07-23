from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Libro:
    id: Optional[int]
    titulo: str
    autor: str
    isbn: str
    editorial: Optional[str]
    anio_publicacion: int
    categoria: Optional[str]
    cantidad_disponible: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: Any) -> "Libro":
        return cls(
            id=row["id"],
            titulo=row["titulo"],
            autor=row["autor"],
            isbn=row["isbn"],
            editorial=row["editorial"],
            anio_publicacion=row["anio_publicacion"],
            categoria=row["categoria"],
            cantidad_disponible=row["cantidad_disponible"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.isbn,
            "editorial": self.editorial,
            "anio_publicacion": self.anio_publicacion,
            "categoria": self.categoria,
            "cantidad_disponible": self.cantidad_disponible,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
