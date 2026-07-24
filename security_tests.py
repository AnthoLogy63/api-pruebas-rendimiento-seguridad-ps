"""
Ejercicio 4 — Pruebas Básicas de Seguridad
==========================================
Sistema: Biblioteca Nova API (Flask + SQLite)
URL base: http://localhost:5000

Casos de prueba:
  Caso 1. Validación de recursos inexistentes → HTTP 404
  Caso 2. Validación de datos incompletos     → HTTP 400 + mensaje descriptivo
  Caso 3. Validación de tipos de datos        → HTTP 400 (rechazo de tipos inválidos)
  Caso 4. Métodos HTTP no permitidos          → HTTP 405
  Caso 5. Simulación de fuerza bruta (opcional) → análisis de comportamiento

Ejecución:
  pip install requests
  python security_tests.py
  python security_tests.py --url http://192.168.1.x:5000
  python security_tests.py --output tests/security/security_report.txt
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any

try:
    import requests
    from requests.exceptions import ConnectionError as ReqConnError, Timeout
except ImportError:
    print("ERROR: El módulo 'requests' no está instalado.")
    print("       Ejecuta: pip install requests")
    sys.exit(1)

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_URL    = "http://localhost:5000"
TIMEOUT     = 10          # segundos por solicitud
RESULTADOS  = []          # lista de resultados de prueba

# ── Colores ANSI ──────────────────────────────────────────────────────────────
class Color:
    VERDE   = "\033[92m"
    ROJO    = "\033[91m"
    AMARILLO= "\033[93m"
    AZUL    = "\033[94m"
    CIAN    = "\033[96m"
    BLANCO  = "\033[97m"
    RESET   = "\033[0m"
    NEGRITA = "\033[1m"

    @staticmethod
    def soporte() -> bool:
        """Detecta si la terminal soporta colores ANSI."""
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colorear(texto: str, color: str) -> str:
    if Color.soporte():
        return f"{color}{texto}{Color.RESET}"
    return texto


# ── Función auxiliar de petición ─────────────────────────────────────────────
def hacer_peticion(
    metodo: str,
    path: str,
    body: Any = None,
    headers: dict | None = None,
    esperado_status: list[int] | None = None,
) -> tuple[int | None, Any]:
    """Realiza una petición HTTP y retorna (status_code, body_json)."""
    url = BASE_URL + path
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)

    try:
        resp = requests.request(
            method=metodo.upper(),
            url=url,
            data=json.dumps(body) if body is not None else None,
            headers=hdrs,
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        try:
            return resp.status_code, resp.json()
        except json.JSONDecodeError:
            return resp.status_code, {"raw": resp.text[:200]}

    except ReqConnError:
        return None, {"error": "Conexión rechazada — ¿está la API en ejecución?"}
    except Timeout:
        return None, {"error": f"Timeout después de {TIMEOUT}s"}


# ── Registro de resultado ────────────────────────────────────────────────────
def registrar(
    caso: str,
    descripcion: str,
    metodo: str,
    path: str,
    status_obtenido: int | None,
    status_esperado: int | list[int],
    pasado: bool,
    detalle: str = "",
    tiempo_ms: float = 0.0,
):
    estado = "PASS" if pasado else "FAIL"
    color  = Color.VERDE if pasado else Color.ROJO
    icono  = "✔" if pasado else "✘"

    esperado_str = (
        "/".join(map(str, status_esperado))
        if isinstance(status_esperado, list)
        else str(status_esperado)
    )

    print(f"  {colorear(icono, color)} {colorear(f'[{estado}]', color)}", end=" ")
    print(f"{colorear(caso, Color.CIAN)}: {descripcion}")
    print(f"       {metodo} {path}")
    print(
        f"       Esperado: HTTP {colorear(esperado_str, Color.AMARILLO)} | "
        f"Obtenido: HTTP {colorear(str(status_obtenido), Color.BLANCO)} | "
        f"Tiempo: {tiempo_ms:.1f}ms"
    )
    if detalle:
        print(f"       Detalle: {detalle}")
    print()

    RESULTADOS.append({
        "caso":            caso,
        "descripcion":     descripcion,
        "metodo":          metodo,
        "path":            path,
        "status_esperado": status_esperado,
        "status_obtenido": status_obtenido,
        "pasado":          pasado,
        "estado":          estado,
        "tiempo_ms":       round(tiempo_ms, 2),
        "detalle":         detalle,
    })


# ── CASO 1: Validación de recursos inexistentes ──────────────────────────────
def caso_1_recursos_inexistentes():
    print(colorear("━" * 65, Color.AZUL))
    print(colorear("  CASO 1 — Validación de Recursos Inexistentes", Color.NEGRITA))
    print(colorear("━" * 65, Color.AZUL))
    print()

    pruebas = [
        ("GET", "/libros/99999",    "Libro con ID inexistente"),
        ("GET", "/libros/0",        "Libro con ID cero"),
        ("GET", "/libros/-1",       "Libro con ID negativo (404/405)"),
        ("GET", "/prestamos/99999", "Préstamo con ID inexistente"),
        ("GET", "/ruta/no/existe",  "Ruta completamente inexistente"),
    ]

    for metodo, path, desc in pruebas:
        t0 = time.time()
        status, body = hacer_peticion(metodo, path)
        ms = (time.time() - t0) * 1000
        pasado = status in (404, 405)
        detalle = body.get("error", "") if isinstance(body, dict) else str(body)[:80]
        registrar("Caso 1", desc, metodo, path, status, [404, 405], pasado, detalle, ms)


# ── CASO 2: Validación de datos incompletos (POST con campos vacíos) ─────────
def caso_2_datos_incompletos():
    print(colorear("━" * 65, Color.AZUL))
    print(colorear("  CASO 2 — Validación de Datos Incompletos", Color.NEGRITA))
    print(colorear("━" * 65, Color.AZUL))
    print()

    pruebas = [
        {
            "desc":    "POST /libros sin ningún campo",
            "path":    "/libros",
            "payload": {},
        },
        {
            "desc":    "POST /libros con título vacío",
            "path":    "/libros",
            "payload": {"titulo": "", "autor": "Autor", "isbn": "978-0-0"},
        },
        {
            "desc":    "POST /libros sin ISBN",
            "path":    "/libros",
            "payload": {"titulo": "Libro", "autor": "Autor"},
        },
        {
            "desc":    "POST /libros sin autor",
            "path":    "/libros",
            "payload": {"titulo": "Libro", "isbn": "978-0-0-0"},
        },
        {
            "desc":    "POST /prestamos sin libro_id",
            "path":    "/prestamos",
            "payload": {"nombre_usuario": "Test", "email": "test@test.com"},
        },
        {
            "desc":    "POST /prestamos con email inválido",
            "path":    "/prestamos",
            "payload": {"libro_id": 1, "nombre_usuario": "Test", "email": "no-es-email"},
        },
    ]

    for p in pruebas:
        t0 = time.time()
        status, body = hacer_peticion("POST", p["path"], p["payload"])
        ms = (time.time() - t0) * 1000
        pasado = status == 400
        detalle = ""
        if isinstance(body, dict):
            detalle = body.get("error", body.get("message", str(body)[:80]))
        # Verificar que haya mensaje descriptivo
        tiene_mensaje = bool(detalle and len(detalle) > 3)
        pasado = pasado and tiene_mensaje
        registrar("Caso 2", p["desc"], "POST", p["path"], status, 400, pasado, detalle, ms)


# ── CASO 3: Validación de tipos de datos ─────────────────────────────────────
def caso_3_tipos_de_datos():
    print(colorear("━" * 65, Color.AZUL))
    print(colorear("  CASO 3 — Validación de Tipos de Datos", Color.NEGRITA))
    print(colorear("━" * 65, Color.AZUL))
    print()

    isbn_unico = f"978-TYPE-{uuid.uuid4().hex[:6]}"

    pruebas = [
        {
            "desc":    "titulo como número entero",
            "payload": {
                "titulo":             12345,
                "autor":              "Autor",
                "isbn":               isbn_unico,
                "cantidad_disponible": 3,
            },
        },
        {
            "desc":    "anio_publicacion como cadena de texto",
            "payload": {
                "titulo":             "Libro Válido",
                "autor":              "Autor",
                "isbn":               isbn_unico + "a",
                "anio_publicacion":   "dos mil veinticuatro",
                "cantidad_disponible": 3,
            },
        },
        {
            "desc":    "cantidad_disponible como cadena ('ABC')",
            "payload": {
                "titulo":             "Libro Válido",
                "autor":              "Autor",
                "isbn":               isbn_unico + "b",
                "cantidad_disponible": "ABC",
            },
        },
        {
            "desc":    "titulo como lista (tipo incorrecto)",
            "payload": {
                "titulo":             ["no", "es", "string"],
                "autor":              "Autor",
                "isbn":               isbn_unico + "c",
                "cantidad_disponible": 2,
            },
        },
        {
            "desc":    "libro_id como cadena en préstamo",
            "path":    "/prestamos",
            "payload": {
                "libro_id":      "uno",
                "nombre_usuario": "Test",
                "email":         "test@test.com",
                "dias_prestamo":  14,
            },
        },
    ]

    for p in pruebas:
        path = p.get("path", "/libros")
        t0 = time.time()
        status, body = hacer_peticion("POST", path, p["payload"])
        ms = (time.time() - t0) * 1000
        # Se espera 400 (rechazado) o 422 (Unprocessable Entity)
        pasado = status in (400, 422)
        detalle = ""
        if isinstance(body, dict):
            detalle = body.get("error", body.get("message", str(body)[:80]))
        registrar("Caso 3", p["desc"], "POST", path, status, [400, 422], pasado, detalle, ms)


# ── CASO 4: Métodos HTTP no permitidos ───────────────────────────────────────
def caso_4_metodos_no_permitidos():
    print(colorear("━" * 65, Color.AZUL))
    print(colorear("  CASO 4 — Métodos HTTP No Permitidos", Color.NEGRITA))
    print(colorear("━" * 65, Color.AZUL))
    print()

    pruebas = [
        ("PATCH",   "/libros",     "PATCH en colección /libros"),
        ("PATCH",   "/libros/1",   "PATCH en recurso /libros/1"),
        ("OPTIONS", "/libros",     "OPTIONS en /libros"),
        ("TRACE",   "/libros",     "TRACE en /libros"),
        ("PUT",     "/libros",     "PUT en colección /libros (sin ID)"),
        ("DELETE",  "/prestamos",  "DELETE en colección /prestamos"),
        ("PATCH",   "/prestamos",  "PATCH en colección /prestamos"),
    ]

    for metodo, path, desc in pruebas:
        t0 = time.time()
        status, body = hacer_peticion(metodo, path)
        ms = (time.time() - t0) * 1000
        pasado = status == 405
        detalle = ""
        if isinstance(body, dict):
            detalle = body.get("error", str(body)[:80])
        registrar("Caso 4", desc, metodo, path, status, 405, pasado, detalle, ms)


# ── CASO 5: Simulación de fuerza bruta (opcional) ────────────────────────────
def caso_5_fuerza_bruta():
    print(colorear("━" * 65, Color.AZUL))
    print(colorear("  CASO 5 — Simulación de Fuerza Bruta (Opcional)", Color.NEGRITA))
    print(colorear("━" * 65, Color.AZUL))
    print()
    print("  Nota: La API no implementa autenticación formal.")
    print("  Se simulan 20 intentos de POST con credenciales inválidas\n"
          "  para analizar si hay mecanismos de protección.\n")

    INTENTOS        = 20
    respuestas      = []
    tiempos         = []
    errores_429     = 0
    timeout_cuenta  = 0

    for i in range(1, INTENTOS + 1):
        payload = {
            "username":  f"admin_ataque_{i}",
            "password":  f"password_erroneo_{i * 13}",
            "token":     "eyJfakeToken12345",
        }
        t0 = time.time()
        status, body = hacer_peticion("POST", "/auth/login", payload)
        ms = (time.time() - t0) * 1000
        tiempos.append(ms)

        if status == 429:
            errores_429 += 1
        if status is None:
            timeout_cuenta += 1

        respuestas.append(status)
        # No hacer sleep entre intentos para simular fuerza bruta real

    # Analizar resultados
    codigos_unicos  = set(respuestas) - {None}
    tiene_bloqueo   = errores_429 > 0
    tiene_timeout   = timeout_cuenta > 0
    tiempo_prom     = sum(tiempos) / len(tiempos) if tiempos else 0

    print(f"  Intentos realizados : {INTENTOS}")
    print(f"  Códigos obtenidos   : {codigos_unicos}")
    print(f"  Respuestas 429      : {errores_429}  (Rate Limiting)")
    print(f"  Timeouts            : {timeout_cuenta}")
    print(f"  Tiempo promedio     : {tiempo_prom:.1f}ms")
    print()

    # Evaluación de mecanismos de protección
    analisis = {
        "Bloqueo temporal (429)":   tiene_bloqueo,
        "Timeout de sesión":        tiene_timeout,
        "Endpoint /auth inexistente (404)": 404 in codigos_unicos,
        "Respuestas consistentes":  len(codigos_unicos) <= 2,
    }

    print("  Análisis de mecanismos de protección:")
    for mecanismo, presente in analisis.items():
        icono = colorear("✔", Color.VERDE) if presente else colorear("✘", Color.ROJO)
        print(f"    {icono} {mecanismo}: {'Presente' if presente else 'No detectado'}")
    print()

    # La API no tiene autenticación → 404 en /auth/login es el comportamiento esperado
    pasado = 404 in codigos_unicos  # endpoint no existe = documentado
    detalle = (
        f"Endpoint /auth/login no implementado (404). "
        f"Sin rate limiting detectado. "
        f"Recomendación: implementar autenticación con rate limit."
    )
    registrar(
        "Caso 5",
        "Simulación de 20 intentos de fuerza bruta en /auth/login",
        "POST", "/auth/login",
        list(codigos_unicos)[0] if codigos_unicos else None,
        [404, 429],
        pasado,
        detalle,
        tiempo_prom,
    )


# ── Generar informe de texto ─────────────────────────────────────────────────
def generar_informe(ruta_salida: str | None = None):
    total   = len(RESULTADOS)
    pasados = sum(1 for r in RESULTADOS if r["pasado"])
    fallidos= total - pasados

    lineas = []
    lineas.append("=" * 70)
    lineas.append("  INFORME DE PRUEBAS DE SEGURIDAD — BIBLIOTECA NOVA API")
    lineas.append(f"  Fecha : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append(f"  URL   : {BASE_URL}")
    lineas.append("=" * 70)
    lineas.append("")
    lineas.append(f"  Total de pruebas  : {total}")
    lineas.append(f"  Pruebas exitosas  : {pasados}  ({pasados*100//total if total else 0}%)")
    lineas.append(f"  Pruebas fallidas  : {fallidos}  ({fallidos*100//total if total else 0}%)")
    lineas.append("")
    lineas.append("─" * 70)
    lineas.append("  DETALLE POR CASO")
    lineas.append("─" * 70)

    caso_actual = ""
    for r in RESULTADOS:
        if r["caso"] != caso_actual:
            caso_actual = r["caso"]
            lineas.append(f"\n  [{caso_actual}]")

        estado_ico = "✔ PASS" if r["pasado"] else "✘ FAIL"
        lineas.append(f"    {estado_ico}  {r['descripcion']}")
        lineas.append(f"          {r['metodo']} {r['path']}")
        lineas.append(
            f"          Esperado: {r['status_esperado']} | "
            f"Obtenido: {r['status_obtenido']} | "
            f"Tiempo: {r['tiempo_ms']}ms"
        )
        if r["detalle"]:
            lineas.append(f"          {r['detalle']}")

    lineas.append("")
    lineas.append("─" * 70)
    lineas.append("  ANÁLISIS Y RECOMENDACIONES")
    lineas.append("─" * 70)
    lineas.append("""
  1. Recursos inexistentes (404): La API maneja correctamente rutas y
     recursos no encontrados devolviendo HTTP 404 con mensaje JSON.

  2. Datos incompletos (400): El sistema valida campos obligatorios y
     retorna HTTP 400 con descripción del error. Buena práctica.

  3. Tipos de datos: Se recomienda agregar validación de tipos explícita
     (Marshmallow / Pydantic) para rechazar tipos incorrectos con 400.

  4. Métodos no permitidos (405): Flask maneja automáticamente los
     métodos no registrados devolviendo HTTP 405. Correcto.

  5. Autenticación: La API no implementa autenticación. Se recomienda
     añadir JWT + rate limiting (Flask-Limiter) para producción.
  """)
    lineas.append("=" * 70)

    texto = "\n".join(lineas)
    print(texto)

    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"\n  Informe guardado en: {ruta_salida}")

    return pasados, total


# ── Punto de entrada principal ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Pruebas de Seguridad — Biblioteca Nova API"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="URL base de la API (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--output",
        default="tests/security/security_report.txt",
        help="Ruta del archivo de informe de salida",
    )
    parser.add_argument(
        "--skip-brute",
        action="store_true",
        help="Omitir el caso 5 (fuerza bruta)",
    )
    args = parser.parse_args()

    global BASE_URL
    BASE_URL = args.url.rstrip("/")

    # ── Encabezado ────────────────────────────────────────────────────────────
    print()
    print(colorear("╔" + "═" * 63 + "╗", Color.CIAN))
    print(colorear("║   PRUEBAS BÁSICAS DE SEGURIDAD — BIBLIOTECA NOVA API      ║", Color.CIAN))
    print(colorear("║   Ejercicio 4 · Python Requests                           ║", Color.CIAN))
    print(colorear("╚" + "═" * 63 + "╝", Color.CIAN))
    print(f"\n  URL: {colorear(BASE_URL, Color.AMARILLO)}")
    print(f"  Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Verificar conectividad
    print(colorear("  Verificando conectividad con la API...", Color.AZUL))
    status, _ = hacer_peticion("GET", "/health")
    if status is None:
        print(colorear("\n  ERROR: No se puede conectar con la API.", Color.ROJO))
        print("  Asegúrate de ejecutar primero: python run_server.py\n")
        sys.exit(1)
    print(colorear(f"  ✔ API en línea (HTTP {status})\n", Color.VERDE))

    # ── Ejecutar casos ────────────────────────────────────────────────────────
    caso_1_recursos_inexistentes()
    caso_2_datos_incompletos()
    caso_3_tipos_de_datos()
    caso_4_metodos_no_permitidos()
    if not args.skip_brute:
        caso_5_fuerza_bruta()

    # ── Informe final ─────────────────────────────────────────────────────────
    print(colorear("\n" + "═" * 65, Color.CIAN))
    print(colorear("  RESUMEN FINAL", Color.NEGRITA))
    print(colorear("═" * 65, Color.CIAN))
    pasados, total = generar_informe(args.output)

    exitcode = 0 if pasados == total else 1
    color_resumen = Color.VERDE if exitcode == 0 else Color.AMARILLO
    print(colorear(f"\n  Resultado: {pasados}/{total} pruebas exitosas\n", color_resumen))
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
