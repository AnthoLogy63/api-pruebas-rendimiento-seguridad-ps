from typing import Optional

from database.db import get_connection
from models.prestamo import Prestamo

SELECT_BASE = """
    SELECT
        p.*,
        l.titulo AS libro_titulo,
        l.autor AS libro_autor
    FROM prestamos p
    INNER JOIN libros l ON l.id = p.libro_id
"""


class PrestamoRepository:
    def find_all(self) -> list[Prestamo]:
        conn = get_connection()
        try:
            rows = conn.execute(
                f"{SELECT_BASE} ORDER BY p.id DESC"
            ).fetchall()
            return [Prestamo.from_row(row) for row in rows]
        finally:
            conn.close()

    def find_by_id(self, prestamo_id: int) -> Optional[Prestamo]:
        conn = get_connection()
        try:
            row = conn.execute(
                f"{SELECT_BASE} WHERE p.id = ?", (prestamo_id,)
            ).fetchone()
            return Prestamo.from_row(row) if row else None
        finally:
            conn.close()

    def find_activos(self) -> list[Prestamo]:
        conn = get_connection()
        try:
            rows = conn.execute(
                f"{SELECT_BASE} WHERE p.estado = 'activo' ORDER BY p.fecha_devolucion_esperada ASC"
            ).fetchall()
            return [Prestamo.from_row(row) for row in rows]
        finally:
            conn.close()

    def count_activos_by_libro(self, libro_id: int) -> int:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT COUNT(*) AS total FROM prestamos
                WHERE libro_id = ? AND estado = 'activo'
                """,
                (libro_id,),
            ).fetchone()
            return row["total"]
        finally:
            conn.close()

    def count_by_libro(self, libro_id: int) -> int:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM prestamos WHERE libro_id = ?",
                (libro_id,),
            ).fetchone()
            return row["total"]
        finally:
            conn.close()

    def create(self, data: dict) -> Prestamo:
        conn = get_connection()
        try:
            conn.execute("BEGIN")
            libro = conn.execute(
                "SELECT id, cantidad_disponible FROM libros WHERE id = ?",
                (data["libro_id"],),
            ).fetchone()
            if libro is None:
                conn.execute("ROLLBACK")
                return None  # type: ignore[return-value]

            if libro["cantidad_disponible"] <= 0:
                conn.execute("ROLLBACK")
                raise ValueError("sin_stock")

            cursor = conn.execute(
                """
                INSERT INTO prestamos (
                    libro_id, nombre_usuario, email,
                    fecha_prestamo, fecha_devolucion_esperada, estado
                ) VALUES (?, ?, ?, datetime('now'), ?, 'activo')
                """,
                (
                    data["libro_id"],
                    data["nombre_usuario"],
                    data["email"],
                    data["fecha_devolucion_esperada"],
                ),
            )
            conn.execute(
                """
                UPDATE libros
                SET cantidad_disponible = cantidad_disponible - 1,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (data["libro_id"],),
            )
            conn.commit()
            prestamo_id = cursor.lastrowid
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

        prestamo = self.find_by_id(prestamo_id)
        if prestamo is None:
            raise RuntimeError("No se pudo recuperar el préstamo creado")
        return prestamo

    def devolver(self, prestamo_id: int) -> Optional[Prestamo]:
        conn = get_connection()
        try:
            conn.execute("BEGIN")
            prestamo = conn.execute(
                "SELECT id, libro_id, estado FROM prestamos WHERE id = ?",
                (prestamo_id,),
            ).fetchone()
            if prestamo is None:
                conn.execute("ROLLBACK")
                return None
            if prestamo["estado"] != "activo":
                conn.execute("ROLLBACK")
                raise ValueError("ya_devuelto")

            conn.execute(
                """
                UPDATE prestamos
                SET estado = 'devuelto',
                    fecha_devolucion_real = datetime('now')
                WHERE id = ?
                """,
                (prestamo_id,),
            )
            conn.execute(
                """
                UPDATE libros
                SET cantidad_disponible = cantidad_disponible + 1,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (prestamo["libro_id"],),
            )
            conn.commit()
        except Exception:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

        return self.find_by_id(prestamo_id)

    def get_estadisticas(self) -> dict:
        conn = get_connection()
        try:
            total = conn.execute(
                "SELECT COUNT(*) AS total FROM prestamos"
            ).fetchone()["total"]
            activos = conn.execute(
                "SELECT COUNT(*) AS total FROM prestamos WHERE estado = 'activo'"
            ).fetchone()["total"]
            devueltos = conn.execute(
                "SELECT COUNT(*) AS total FROM prestamos WHERE estado = 'devuelto'"
            ).fetchone()["total"]
            vencidos = conn.execute(
                """
                SELECT COUNT(*) AS total FROM prestamos
                WHERE estado = 'activo'
                  AND datetime(fecha_devolucion_esperada) < datetime('now')
                """
            ).fetchone()["total"]

            return {
                "total_prestamos": total,
                "prestamos_activos": activos,
                "prestamos_devueltos": devueltos,
                "prestamos_vencidos": vencidos,
            }
        finally:
            conn.close()
