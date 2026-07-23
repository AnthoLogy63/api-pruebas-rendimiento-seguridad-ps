"""Script de prueba rápida para verificar todos los endpoints."""
import json
import uuid
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://localhost:5000"


def request(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body or str(e)}


def main():
    tests = []

    # Estado de la biblioteca
    code, data = request("GET", "/biblioteca/estado")
    tests.append(("GET /biblioteca/estado", code == 200, code))

    # Alias técnico para JMeter/K6
    code, data = request("GET", "/health")
    tests.append(("GET /health (alias)", code == 200, code))

    # Panel web
    req = urllib.request.Request(BASE + "/")
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode()
            tests.append(("GET / (panel web)", resp.status == 200 and "Biblioteca Nova" in html, resp.status))
    except urllib.error.HTTPError as e:
        tests.append(("GET / (panel web)", False, e.code))

    # Create book
    unique_isbn = f"978-TEST-{uuid.uuid4().hex[:8]}"
    libro = {
        "titulo": "Cien años de soledad",
        "autor": "Gabriel García Márquez",
        "isbn": unique_isbn,
        "editorial": "Sudamericana",
        "anio_publicacion": 1967,
        "categoria": "Novela",
        "cantidad_disponible": 5,
    }
    code, data = request("POST", "/libros", libro)
    tests.append(("POST /libros", code == 201, code))
    libro_id = data["data"]["id"]

    # List books
    code, data = request("GET", "/libros")
    tests.append(("GET /libros", code == 200 and data["total"] >= 1, code))

    # Get by ID
    code, data = request("GET", f"/libros/{libro_id}")
    tests.append(("GET /libros/<id>", code == 200, code))

    # Update
    libro["cantidad_disponible"] = 10
    code, data = request("PUT", f"/libros/{libro_id}", libro)
    tests.append(("PUT /libros/<id>", code == 200, code))

    # Search
    query = urllib.parse.urlencode({"autor": "García"})
    code, data = request("GET", f"/libros/buscar?{query}")
    tests.append(("GET /libros/buscar", code == 200, code))

    # Categories
    code, data = request("GET", "/libros/categorias")
    tests.append(("GET /libros/categorias", code == 200, code))

    # Stats
    code, data = request("GET", "/libros/estadisticas")
    tests.append(("GET /libros/estadisticas", code == 200, code))

    # Delete (before creating prestamos on this book)
    code, data = request("DELETE", f"/libros/{libro_id}")
    tests.append(("DELETE /libros/<id>", code == 200, code))

    # Delete not found
    code, data = request("DELETE", f"/libros/{libro_id}")
    tests.append(("DELETE not found (404)", code == 404, code))

    # Create book for prestamo tests
    libro2_isbn = f"978-PREST-{uuid.uuid4().hex[:8]}"
    libro2 = {**libro, "isbn": libro2_isbn, "cantidad_disponible": 3}
    code, data = request("POST", "/libros", libro2)
    tests.append(("POST /libros (prestamo)", code == 201, code))
    libro2_id = data.get("data", {}).get("id")

    if libro2_id:
        prestamo_payload = {
            "libro_id": libro2_id,
            "nombre_usuario": "Test User",
            "email": "test@email.com",
            "dias_prestamo": 14,
        }
        code, data = request("POST", "/prestamos", prestamo_payload)
        tests.append(("POST /prestamos", code == 201, code))
        prestamo_id = data.get("data", {}).get("id")

        if prestamo_id:
            code, data = request("GET", f"/prestamos/{prestamo_id}")
            tests.append(("GET /prestamos/<id>", code == 200, code))

            code, data = request("GET", "/prestamos/activos")
            tests.append(("GET /prestamos/activos", code == 200, code))

            code, data = request("GET", "/prestamos")
            tests.append(("GET /prestamos", code == 200, code))

            code, data = request("PUT", f"/prestamos/{prestamo_id}/devolver")
            tests.append(("PUT /prestamos/devolver", code == 200, code))

            code, data = request("DELETE", f"/libros/{libro2_id}")
            tests.append(("DELETE con historial (409)", code == 409, code))

    code, data = request("GET", "/prestamos/estadisticas")
    tests.append(("GET /prestamos/estadisticas", code == 200, code))

    # Error: prestamo invalid email
    code, data = request("POST", "/prestamos", {"libro_id": 1, "nombre_usuario": "X", "email": "bad"})
    tests.append(("POST prestamo invalid (400)", code == 400, code))

    # Error: invalid data
    code, data = request("POST", "/libros", {"titulo": "", "autor": "X", "isbn": "123"})
    tests.append(("POST invalid (400)", code == 400, code))

    # Error: not found
    code, data = request("GET", "/libros/99999")
    tests.append(("GET not found (404)", code == 404, code))

    print("\n=== Resultados de pruebas ===")
    passed = 0
    for name, ok, code in tests:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name} (HTTP {code})")
        if ok:
            passed += 1

    print(f"\n{passed}/{len(tests)} pruebas exitosas")
    return passed == len(tests)


if __name__ == "__main__":
    import sys

    sys.exit(0 if main() else 1)
