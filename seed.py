"""
Seed de datos de prueba para Biblioteca Nova.

Uso:
    python seed.py          # Inserta datos si la BD está vacía
    python seed.py --reset  # Borra todo y vuelve a cargar
"""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.db import DATABASE_PATH, get_connection, init_db

LIBROS = [
    {
        "titulo": "Cien años de soledad",
        "autor": "Gabriel García Márquez",
        "isbn": "978-0307474728",
        "editorial": "Sudamericana",
        "anio_publicacion": 1967,
        "categoria": "Novela",
        "cantidad_disponible": 5,
    },
    {
        "titulo": "El Quijote de la Mancha",
        "autor": "Miguel de Cervantes",
        "isbn": "978-8420412146",
        "editorial": "Alfaguara",
        "anio_publicacion": 1605,
        "categoria": "Clásico",
        "cantidad_disponible": 3,
    },
    {
        "titulo": "1984",
        "autor": "George Orwell",
        "isbn": "978-0451524935",
        "editorial": "Debolsillo",
        "anio_publicacion": 1949,
        "categoria": "Ciencia Ficción",
        "cantidad_disponible": 8,
    },
    {
        "titulo": "Crónica de una muerte anunciada",
        "autor": "Gabriel García Márquez",
        "isbn": "978-8497592489",
        "editorial": "Debolsillo",
        "anio_publicacion": 1981,
        "categoria": "Novela",
        "cantidad_disponible": 4,
    },
    {
        "titulo": "La sombra del viento",
        "autor": "Carlos Ruiz Zafón",
        "isbn": "978-8408043640",
        "editorial": "Planeta",
        "anio_publicacion": 2001,
        "categoria": "Novela",
        "cantidad_disponible": 6,
    },
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "isbn": "978-1451673319",
        "editorial": "Debolsillo",
        "anio_publicacion": 1953,
        "categoria": "Ciencia Ficción",
        "cantidad_disponible": 7,
    },
    {
        "titulo": "El nombre del viento",
        "autor": "Patrick Rothfuss",
        "isbn": "978-0345532679",
        "editorial": "DAW",
        "anio_publicacion": 2007,
        "categoria": "Fantasía",
        "cantidad_disponible": 5,
    },
    {
        "titulo": "Orgullo y prejuicio",
        "autor": "Jane Austen",
        "isbn": "978-8491050220",
        "editorial": "Alma",
        "anio_publicacion": 1813,
        "categoria": "Romance",
        "cantidad_disponible": 4,
    },
    {
        "titulo": "Dune",
        "autor": "Frank Herbert",
        "isbn": "978-0441172719",
        "editorial": "Chilton Books",
        "anio_publicacion": 1965,
        "categoria": "Ciencia Ficción",
        "cantidad_disponible": 6,
    },
    {
        "titulo": "Los miserables",
        "autor": "Victor Hugo",
        "isbn": "978-8491050299",
        "editorial": "Alma",
        "anio_publicacion": 1862,
        "categoria": "Clásico",
        "cantidad_disponible": 3,
    },
    {
        "titulo": "El aleph",
        "autor": "Jorge Luis Borges",
        "isbn": "978-9500396702",
        "editorial": "Emecé",
        "anio_publicacion": 1949,
        "categoria": "Cuento",
        "cantidad_disponible": 5,
    },
    {
        "titulo": "Harry Potter y la piedra filosofal",
        "autor": "J.K. Rowling",
        "isbn": "978-8478884452",
        "editorial": "Salamandra",
        "anio_publicacion": 1997,
        "categoria": "Fantasía",
        "cantidad_disponible": 10,
    },
    {
        "titulo": "Rayuela",
        "autor": "Julio Cortázar",
        "isbn": "978-8466331920",
        "editorial": "Alfaguara",
        "anio_publicacion": 1963,
        "categoria": "Novela",
        "cantidad_disponible": 4,
    },
    {
        "titulo": "Sapiens",
        "autor": "Yuval Noah Harari",
        "isbn": "978-8499926224",
        "editorial": "Debate",
        "anio_publicacion": 2011,
        "categoria": "Ensayo",
        "cantidad_disponible": 6,
    },
    {
        "titulo": "Clean Code",
        "autor": "Robert C. Martin",
        "isbn": "978-0132350884",
        "editorial": "Prentice Hall",
        "anio_publicacion": 2008,
        "categoria": "Tecnología",
        "cantidad_disponible": 8,
    },
]

PRESTAMOS = [
    {
        "isbn": "978-0307474728",
        "nombre_usuario": "Ana Martínez",
        "email": "ana.martinez@email.com",
        "dias_prestamo": 14,
        "estado": "activo",
    },
    {
        "isbn": "978-0451524935",
        "nombre_usuario": "Carlos López",
        "email": "carlos.lopez@email.com",
        "dias_prestamo": 7,
        "estado": "activo",
    },
    {
        "isbn": "978-0345532679",
        "nombre_usuario": "María González",
        "email": "maria.gonzalez@email.com",
        "dias_prestamo": -5,
        "estado": "activo",
    },
    {
        "isbn": "978-8478884452",
        "nombre_usuario": "Pedro Sánchez",
        "email": "pedro.sanchez@email.com",
        "dias_prestamo": 14,
        "estado": "devuelto",
    },
    {
        "isbn": "978-0132350884",
        "nombre_usuario": "Laura Fernández",
        "email": "laura.fernandez@email.com",
        "dias_prestamo": 10,
        "estado": "activo",
    },
    {
        "isbn": "978-8499926224",
        "nombre_usuario": "Diego Ramírez",
        "email": "diego.ramirez@email.com",
        "dias_prestamo": 21,
        "estado": "activo",
    },
]


def reset_database(conn):
    conn.execute("DELETE FROM prestamos")
    conn.execute("DELETE FROM libros")
    conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('libros', 'prestamos')")
    conn.commit()


def seed_libros(conn) -> dict[str, int]:
    isbn_to_id = {}
    for libro in LIBROS:
        cursor = conn.execute(
            """
            INSERT INTO libros (
                titulo, autor, isbn, editorial,
                anio_publicacion, categoria, cantidad_disponible
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                libro["titulo"],
                libro["autor"],
                libro["isbn"],
                libro["editorial"],
                libro["anio_publicacion"],
                libro["categoria"],
                libro["cantidad_disponible"],
            ),
        )
        isbn_to_id[libro["isbn"]] = cursor.lastrowid
    conn.commit()
    return isbn_to_id


def seed_prestamos(conn, isbn_to_id: dict[str, int]):
    now = datetime.now()

    for prestamo in PRESTAMOS:
        libro_id = isbn_to_id[prestamo["isbn"]]
        dias = prestamo["dias_prestamo"]
        fecha_prestamo = now - timedelta(days=abs(dias) if dias < 0 else 3)
        fecha_devolucion = fecha_prestamo + timedelta(days=abs(dias) if dias > 0 else 14)
        estado = prestamo["estado"]

        conn.execute(
            "UPDATE libros SET cantidad_disponible = cantidad_disponible - 1 WHERE id = ?",
            (libro_id,),
        )

        if estado == "devuelto":
            conn.execute(
                """
                INSERT INTO prestamos (
                    libro_id, nombre_usuario, email,
                    fecha_prestamo, fecha_devolucion_esperada,
                    fecha_devolucion_real, estado
                ) VALUES (?, ?, ?, ?, ?, datetime('now'), 'devuelto')
                """,
                (
                    libro_id,
                    prestamo["nombre_usuario"],
                    prestamo["email"],
                    fecha_prestamo.strftime("%Y-%m-%d %H:%M:%S"),
                    fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.execute(
                "UPDATE libros SET cantidad_disponible = cantidad_disponible + 1 WHERE id = ?",
                (libro_id,),
            )
        else:
            conn.execute(
                """
                INSERT INTO prestamos (
                    libro_id, nombre_usuario, email,
                    fecha_prestamo, fecha_devolucion_esperada, estado
                ) VALUES (?, ?, ?, ?, ?, 'activo')
                """,
                (
                    libro_id,
                    prestamo["nombre_usuario"],
                    prestamo["email"],
                    fecha_prestamo.strftime("%Y-%m-%d %H:%M:%S"),
                    fecha_devolucion.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )

    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Seed de Biblioteca Nova")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Elimina todos los datos y vuelve a cargar",
    )
    args = parser.parse_args()

    init_db()
    conn = get_connection()

    try:
        count = conn.execute("SELECT COUNT(*) AS c FROM libros").fetchone()["c"]

        if count > 0 and not args.reset:
            print(f"La base de datos ya tiene {count} libros.")
            print("Usa --reset para borrar y volver a cargar.")
            return

        if args.reset:
            print("Reiniciando base de datos...")
            reset_database(conn)

        print("Insertando libros...")
        isbn_to_id = seed_libros(conn)
        print(f"  {len(LIBROS)} libros insertados.")

        print("Insertando préstamos...")
        seed_prestamos(conn, isbn_to_id)
        print(f"  {len(PRESTAMOS)} préstamos insertados.")

        total_libros = conn.execute("SELECT COUNT(*) AS c FROM libros").fetchone()["c"]
        total_prestamos = conn.execute("SELECT COUNT(*) AS c FROM prestamos").fetchone()["c"]
        activos = conn.execute(
            "SELECT COUNT(*) AS c FROM prestamos WHERE estado = 'activo'"
        ).fetchone()["c"]

        print("\nSeed completado.")
        print(f"  Base de datos: {DATABASE_PATH}")
        print(f"  Libros: {total_libros}")
        print(f"  Préstamos: {total_prestamos} ({activos} activos)")
        print("\nEjecuta: python app.py")
        print("Abre: http://localhost:5000")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
