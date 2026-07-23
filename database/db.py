import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "biblioteca.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                editorial TEXT,
                anio_publicacion INTEGER NOT NULL,
                categoria TEXT,
                cantidad_disponible INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_libros_autor ON libros(autor);
            CREATE INDEX IF NOT EXISTS idx_libros_categoria ON libros(categoria);
            CREATE INDEX IF NOT EXISTS idx_libros_isbn ON libros(isbn);

            CREATE TABLE IF NOT EXISTS prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id INTEGER NOT NULL,
                nombre_usuario TEXT NOT NULL,
                email TEXT NOT NULL,
                fecha_prestamo TEXT NOT NULL DEFAULT (datetime('now')),
                fecha_devolucion_esperada TEXT NOT NULL,
                fecha_devolucion_real TEXT,
                estado TEXT NOT NULL DEFAULT 'activo',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (libro_id) REFERENCES libros(id) ON DELETE RESTRICT
            );

            CREATE INDEX IF NOT EXISTS idx_prestamos_libro ON prestamos(libro_id);
            CREATE INDEX IF NOT EXISTS idx_prestamos_estado ON prestamos(estado);
            CREATE INDEX IF NOT EXISTS idx_prestamos_email ON prestamos(email);
            """
        )
        conn.commit()
    finally:
        conn.close()
