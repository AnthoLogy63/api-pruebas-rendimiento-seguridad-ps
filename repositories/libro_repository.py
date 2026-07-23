from typing import Optional

from database.db import get_connection
from models.libro import Libro


class LibroRepository:
    def find_all(self) -> list[Libro]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM libros ORDER BY id ASC"
            ).fetchall()
            return [Libro.from_row(row) for row in rows]
        finally:
            conn.close()

    def find_by_id(self, libro_id: int) -> Optional[Libro]:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM libros WHERE id = ?", (libro_id,)
            ).fetchone()
            return Libro.from_row(row) if row else None
        finally:
            conn.close()

    def find_by_isbn(self, isbn: str) -> Optional[Libro]:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM libros WHERE isbn = ?", (isbn,)
            ).fetchone()
            return Libro.from_row(row) if row else None
        finally:
            conn.close()

    def search(
        self,
        titulo: Optional[str] = None,
        autor: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> list[Libro]:
        query = "SELECT * FROM libros WHERE 1=1"
        params: list = []

        if titulo:
            query += " AND titulo LIKE ?"
            params.append(f"%{titulo}%")
        if autor:
            query += " AND autor LIKE ?"
            params.append(f"%{autor}%")
        if categoria:
            query += " AND categoria LIKE ?"
            params.append(f"%{categoria}%")

        query += " ORDER BY id ASC"

        conn = get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [Libro.from_row(row) for row in rows]
        finally:
            conn.close()

    def create(self, data: dict) -> Libro:
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO libros (
                    titulo, autor, isbn, editorial,
                    anio_publicacion, categoria, cantidad_disponible
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["titulo"],
                    data["autor"],
                    data["isbn"],
                    data.get("editorial"),
                    data["anio_publicacion"],
                    data.get("categoria"),
                    data["cantidad_disponible"],
                ),
            )
            conn.commit()
            libro_id = cursor.lastrowid
        finally:
            conn.close()

        libro = self.find_by_id(libro_id)
        if libro is None:
            raise RuntimeError("No se pudo recuperar el libro creado")
        return libro

    def update(self, libro_id: int, data: dict) -> Optional[Libro]:
        conn = get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE libros SET
                    titulo = ?,
                    autor = ?,
                    isbn = ?,
                    editorial = ?,
                    anio_publicacion = ?,
                    categoria = ?,
                    cantidad_disponible = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    data["titulo"],
                    data["autor"],
                    data["isbn"],
                    data.get("editorial"),
                    data["anio_publicacion"],
                    data.get("categoria"),
                    data["cantidad_disponible"],
                    libro_id,
                ),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
        finally:
            conn.close()

        return self.find_by_id(libro_id)

    def delete(self, libro_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM libros WHERE id = ?", (libro_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_categorias(self) -> list[str]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT DISTINCT categoria FROM libros
                WHERE categoria IS NOT NULL AND categoria != ''
                ORDER BY categoria ASC
                """
            ).fetchall()
            return [row["categoria"] for row in rows]
        finally:
            conn.close()

    def get_estadisticas(self) -> dict:
        conn = get_connection()
        try:
            total = conn.execute(
                "SELECT COUNT(*) AS total FROM libros"
            ).fetchone()["total"]

            disponibles = conn.execute(
                "SELECT COALESCE(SUM(cantidad_disponible), 0) AS total FROM libros"
            ).fetchone()["total"]

            por_categoria = conn.execute(
                """
                SELECT
                    COALESCE(categoria, 'Sin categoría') AS categoria,
                    COUNT(*) AS cantidad
                FROM libros
                GROUP BY categoria
                ORDER BY cantidad DESC
                """
            ).fetchall()

            return {
                "total_libros": total,
                "total_ejemplares_disponibles": disponibles,
                "libros_por_categoria": [
                    {"categoria": row["categoria"], "cantidad": row["cantidad"]}
                    for row in por_categoria
                ],
            }
        finally:
            conn.close()
