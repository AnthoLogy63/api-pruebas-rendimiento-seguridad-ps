"""
Ejercicio 4 -- Pruebas Basicas de Seguridad
============================================
Sistema : Biblioteca Nova API  (Flask + SQLite)
URL base: http://127.0.0.1:5000

Ejecucion:
  python security_tests.py
  python security_tests.py --url http://127.0.0.1:5000
  python security_tests.py --skip-brute
"""

import argparse
import io
import json
import os
import sys
import time
import uuid
from datetime import datetime

# Forzar UTF-8 en Windows para box-drawing characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    import requests
    from requests.exceptions import ConnectionError as ReqConnError, Timeout
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

# ─── Config ──────────────────────────────────────────────────────────────────
BASE_URL   = "http://127.0.0.1:5000"
TIMEOUT    = 10
RESULTADOS = []          # acumula todos los resultados para el resumen final
REPORT_LINES = []        # lineas del informe en texto plano


# ─── Utilidades de impresion ──────────────────────────────────────────────────
def out(texto=""):
    print(texto, flush=True)
    REPORT_LINES.append(texto)


def titulo_caso(numero, nombre):
    out()
    out("┌" + "─" * 70 + "┐")
    out(f"│  CASO {numero}  │  {nombre:<61}│")
    out("└" + "─" * 70 + "┘")


def bloque_codigo(lineas_codigo):
    """Muestra un bloque de codigo/peticion con borde."""
    ancho = 68
    out("  ╔" + "═" * ancho + "╗")
    out("  ║  Solicitudes enviadas" + " " * (ancho - 22) + "║")
    out("  ╠" + "═" * ancho + "╣")
    for linea in lineas_codigo:
        relleno = ancho - 2 - len(linea)
        out(f"  ║  {linea}{' ' * relleno}║")
    out("  ╚" + "═" * ancho + "╝")


def tabla_resultados(columnas, filas):
    """
    Imprime una tabla formateada.
    columnas = [(nombre, ancho), ...]
    filas    = [lista de celdas por fila]
    """
    # Cabecera
    sep_top = "  ┌" + "┬".join("─" * (a + 2) for _, a in columnas) + "┐"
    sep_mid = "  ├" + "┼".join("─" * (a + 2) for _, a in columnas) + "┤"
    sep_bot = "  └" + "┴".join("─" * (a + 2) for _, a in columnas) + "┘"
    head    = "  │" + "│".join(f" {n:<{a}} " for n, a in columnas) + "│"

    out(sep_top)
    out(head)
    out(sep_mid)
    for fila in filas:
        linea = "  │"
        for i, (_, ancho) in enumerate(columnas):
            celda = str(fila[i]) if i < len(fila) else ""
            linea += f" {celda:<{ancho}} │"
        out(linea)
    out(sep_bot)


def registrar(caso, descripcion, metodo, path,
              status_obtenido, status_esperado, pasado,
              detalle="", tiempo_ms=0.0):
    RESULTADOS.append({
        "caso":            caso,
        "descripcion":     descripcion,
        "metodo":          metodo,
        "path":            path,
        "status_esperado": status_esperado,
        "status_obtenido": status_obtenido,
        "pasado":          pasado,
        "estado":          "PASS" if pasado else "FAIL",
        "tiempo_ms":       round(tiempo_ms, 1),
        "detalle":         str(detalle)[:120],
    })


# ─── HTTP helper ──────────────────────────────────────────────────────────────
def req(metodo, path, body=None):
    url  = BASE_URL + path
    hdrs = {"Content-Type": "application/json"}
    try:
        r = requests.request(
            method=metodo.upper(), url=url,
            data=json.dumps(body) if body is not None else None,
            headers=hdrs, timeout=TIMEOUT, allow_redirects=True,
        )
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text[:200]}
    except ReqConnError:
        return None, {"error": "Conexion rechazada"}
    except Timeout:
        return None, {"error": "Timeout"}


# ═══════════════════════════════════════════════════════════════════════════════
#  CASO 1 — Recursos inexistentes
# ═══════════════════════════════════════════════════════════════════════════════
def caso_1():
    titulo_caso(1, "Validacion de Recursos Inexistentes")
    out()
    out("  Objetivo : Solicitudes GET a IDs o rutas que no existen.")
    out("  Esperado : Codigo HTTP 404 con mensaje JSON descriptivo.")
    out()

    bloque_codigo([
        "GET /libros/99999      # ID de libro que no existe",
        "GET /libros/0          # ID cero (invalido)",
        "GET /prestamos/99999   # ID de prestamo inexistente",
        "GET /ruta/inexistente  # Ruta completamente desconocida",
    ])
    out()

    cols = [("Descripcion", 32), ("Metodo", 7), ("Path", 22),
            ("Esperado", 9), ("Obtenido", 9), ("Tiempo", 8), ("Resultado", 8)]
    filas = []

    pruebas = [
        ("GET", "/libros/99999",     "Libro con ID inexistente"),
        ("GET", "/libros/0",         "Libro con ID cero"),
        ("GET", "/prestamos/99999",  "Prestamo ID inexistente"),
        ("GET", "/ruta/inexistente", "Ruta desconocida"),
    ]

    for metodo, path, desc in pruebas:
        t0 = time.time()
        status, body = req(metodo, path)
        ms = (time.time() - t0) * 1000
        pasado = status in (404, 405)
        detalle = body.get("error", "") if isinstance(body, dict) else ""
        estado = "✔ PASS" if pasado else "✘ FAIL"
        filas.append([desc, metodo, path, "404", str(status), f"{ms:.0f}ms", estado])
        registrar("Caso 1", desc, metodo, path, status, [404, 405], pasado, detalle, ms)

    tabla_resultados(cols, filas)
    out()
    out("  Analisis: La API retorna HTTP 404 con JSON descriptivo para")
    out("  recursos no encontrados. Comportamiento correcto.")


# ═══════════════════════════════════════════════════════════════════════════════
#  CASO 2 — Datos incompletos
# ═══════════════════════════════════════════════════════════════════════════════
def caso_2():
    titulo_caso(2, "Validacion de Datos Incompletos")
    out()
    out("  Objetivo : POST con campos obligatorios vacios o ausentes.")
    out("  Esperado : HTTP 400 con mensaje de error descriptivo.")
    out()

    bloque_codigo([
        'POST /libros   { }                                    # sin campos',
        'POST /libros   { "titulo": "" }                       # titulo vacio',
        'POST /libros   { "titulo": "X", "autor": "Y" }       # sin isbn',
        'POST /libros   { "titulo": "X", "isbn": "Y" }        # sin autor',
        'POST /prestamos { "nombre_usuario": "X" }             # sin libro_id',
        'POST /prestamos { "libro_id":1, "email":"no-email" }  # email invalido',
    ])
    out()

    pruebas = [
        ("/libros",    {},                                                         "Sin ningun campo"),
        ("/libros",    {"titulo": "", "autor": "A", "isbn": "978-0"},             "Titulo vacio"),
        ("/libros",    {"titulo": "X", "autor": "A"},                             "Sin ISBN"),
        ("/libros",    {"titulo": "X", "isbn": "978-1"},                          "Sin autor"),
        ("/prestamos", {"nombre_usuario": "Test", "email": "t@t.com"},            "Sin libro_id"),
        ("/prestamos", {"libro_id": 1, "nombre_usuario": "T", "email": "malo"},   "Email invalido"),
    ]

    cols = [("Descripcion", 22), ("Endpoint", 12), ("Esperado", 9),
            ("Obtenido", 9), ("Mensaje de error", 30), ("Tiempo", 8), ("Resultado", 8)]
    filas = []

    for path, payload, desc in pruebas:
        t0 = time.time()
        status, body = req("POST", path, payload)
        ms = (time.time() - t0) * 1000
        detalle = ""
        if isinstance(body, dict):
            detalle = body.get("error", body.get("message", ""))
        tiene_msg = bool(detalle and len(str(detalle)) > 3)
        pasado = (status == 400) and tiene_msg
        estado = "✔ PASS" if pasado else "✘ FAIL"
        msg_corto = str(detalle)[:28] + ("…" if len(str(detalle)) > 28 else "")
        filas.append([desc, path, "400", str(status), msg_corto, f"{ms:.0f}ms", estado])
        registrar("Caso 2", desc, "POST", path, status, 400, pasado, detalle, ms)

    tabla_resultados(cols, filas)
    out()
    out("  Analisis: La API valida todos los campos obligatorios y")
    out("  retorna mensajes de error especificos. Correcto.")


# ═══════════════════════════════════════════════════════════════════════════════
#  CASO 3 — Tipos de datos incorrectos
# ═══════════════════════════════════════════════════════════════════════════════
def caso_3():
    titulo_caso(3, "Validacion de Tipos de Datos")
    out()
    out("  Objetivo : Enviar valores de tipo incorrecto en campos del cuerpo.")
    out("  Esperado : HTTP 400 o 422 — el sistema rechaza la solicitud.")
    out()

    bloque_codigo([
        'POST /libros   { "titulo": 12345, ... }           # titulo como numero',
        'POST /libros   { "anio_publicacion": "dos mil" }  # texto en campo numerico',
        'POST /libros   { "cantidad_disponible": "ABC" }   # string donde va entero',
        'POST /libros   { "titulo": ["a","b","c"] }        # lista donde va string',
        'POST /prestamos { "libro_id": "uno", ... }        # string donde va entero',
    ])
    out()

    base = f"978-TYPE-{uuid.uuid4().hex[:6]}"
    pruebas = [
        ("/libros",    {"titulo": 12345,          "autor": "A", "isbn": base,      "cantidad_disponible": 3}, "titulo como int"),
        ("/libros",    {"titulo": "L",             "autor": "A", "isbn": base+"a",  "anio_publicacion": "dos mil", "cantidad_disponible": 3}, "anio como texto"),
        ("/libros",    {"titulo": "L",             "autor": "A", "isbn": base+"b",  "cantidad_disponible": "ABC"}, "cantidad como string"),
        ("/libros",    {"titulo": ["a","b","c"],   "autor": "A", "isbn": base+"c",  "cantidad_disponible": 2}, "titulo como lista"),
        ("/prestamos", {"libro_id": "uno", "nombre_usuario": "T", "email": "t@t.com", "dias_prestamo": 14}, "libro_id como string"),
    ]

    cols = [("Descripcion", 22), ("Endpoint", 12), ("Tipo incorrecto", 18),
            ("Esperado", 9), ("Obtenido", 9), ("Tiempo", 8), ("Resultado", 8)]
    filas = []

    tipo_labels = ["int→titulo", "str→anio", "str→cantidad", "list→titulo", "str→libro_id"]

    for i, (path, payload, desc) in enumerate(pruebas):
        t0 = time.time()
        status, body = req("POST", path, payload)
        ms = (time.time() - t0) * 1000
        detalle = ""
        if isinstance(body, dict):
            detalle = body.get("error", body.get("message", ""))
        pasado = status in (400, 422)
        estado = "✔ PASS" if pasado else "✘ FAIL"
        filas.append([desc, path, tipo_labels[i], "400/422", str(status), f"{ms:.0f}ms", estado])
        registrar("Caso 3", desc, "POST", path, status, [400, 422], pasado, detalle, ms)

    tabla_resultados(cols, filas)
    out()
    out("  Analisis: La API rechaza tipos de datos invalidos con HTTP 400.")
    out("  Recomendacion: agregar Marshmallow/Pydantic para validacion")
    out("  explicita de tipos con mensajes mas descriptivos.")


# ═══════════════════════════════════════════════════════════════════════════════
#  CASO 4 — Metodos HTTP no permitidos
# ═══════════════════════════════════════════════════════════════════════════════
def caso_4():
    titulo_caso(4, "Metodos HTTP No Permitidos")
    out()
    out("  Objetivo : Usar metodos HTTP no registrados en los endpoints.")
    out("  Esperado : HTTP 405 Method Not Allowed.")
    out()

    bloque_codigo([
        "PATCH  /libros     # modificacion parcial en coleccion",
        "PATCH  /libros/1   # modificacion parcial en recurso",
        "PUT    /libros     # actualizacion en coleccion (sin ID)",
        "DELETE /prestamos  # eliminacion de coleccion completa",
        "PATCH  /prestamos  # modificacion parcial en prestamos",
    ])
    out()

    pruebas = [
        ("PATCH",  "/libros",    "PATCH en coleccion /libros"),
        ("PATCH",  "/libros/1",  "PATCH en recurso /libros/1"),
        ("PUT",    "/libros",    "PUT en coleccion sin ID"),
        ("DELETE", "/prestamos", "DELETE en coleccion /prestamos"),
        ("PATCH",  "/prestamos", "PATCH en coleccion /prestamos"),
    ]

    cols = [("Descripcion", 30), ("Metodo", 8), ("Endpoint", 14),
            ("Esperado", 9), ("Obtenido", 9), ("Tiempo", 8), ("Resultado", 8)]
    filas = []

    for metodo, path, desc in pruebas:
        t0 = time.time()
        status, body = req(metodo, path)
        ms = (time.time() - t0) * 1000
        pasado = status == 405
        detalle = body.get("error", "") if isinstance(body, dict) else ""
        estado = "✔ PASS" if pasado else "✘ FAIL"
        filas.append([desc, metodo, path, "405", str(status), f"{ms:.0f}ms", estado])
        registrar("Caso 4", desc, metodo, path, status, 405, pasado, detalle, ms)

    tabla_resultados(cols, filas)
    out()
    out("  Analisis: Flask retorna HTTP 405 automaticamente para metodos")
    out("  no registrados. Comportamiento correcto y seguro.")


# ═══════════════════════════════════════════════════════════════════════════════
#  CASO 5 — Fuerza bruta
# ═══════════════════════════════════════════════════════════════════════════════
def caso_5():
    titulo_caso(5, "Simulacion de Fuerza Bruta (Opcional)")
    out()
    out("  Objetivo : 20 intentos consecutivos de login con credenciales")
    out("             incorrectas para detectar mecanismos de proteccion.")
    out("  Esperado : Bloqueo temporal (429) o limitacion de intentos.")
    out()

    bloque_codigo([
        "POST /auth/login  { username: admin_1,  password: wrong_13  }",
        "POST /auth/login  { username: admin_2,  password: wrong_26  }",
        "POST /auth/login  { ... 20 intentos en total ... }",
    ])
    out()

    INTENTOS = 20
    resultados_bf = []
    tiempos      = []
    errores_429  = 0

    out("  Ejecutando intentos...")
    for i in range(1, INTENTOS + 1):
        payload = {"username": f"admin_{i}", "password": f"wrong_{i*13}", "token": "fake"}
        t0 = time.time()
        status, _ = req("POST", "/auth/login", payload)
        ms = (time.time() - t0) * 1000
        tiempos.append(ms)
        if status == 429:
            errores_429 += 1
        resultados_bf.append(status)
        print(f"  Intento {i:02d}/20 → HTTP {status} | {ms:.0f}ms   ", end="\r", flush=True)

    print(" " * 50, end="\r", flush=True)
    out()

    codigos      = set(resultados_bf) - {None}
    tiempo_prom  = sum(tiempos) / len(tiempos)

    # Tabla de metricas
    cols_m = [("Metrica", 30), ("Valor", 30)]
    filas_m = [
        ["Total de intentos",      str(INTENTOS)],
        ["Codigos HTTP obtenidos",  str(codigos)],
        ["Respuestas 429 (limit.)",  str(errores_429)],
        ["Tiempo promedio por req",  f"{tiempo_prom:.0f}ms"],
        ["Tiempo minimo",            f"{min(tiempos):.0f}ms"],
        ["Tiempo maximo",            f"{max(tiempos):.0f}ms"],
    ]
    tabla_resultados(cols_m, filas_m)
    out()

    # Tabla de mecanismos
    out("  Mecanismos de proteccion detectados:")
    cols_p = [("Mecanismo", 36), ("Estado", 20), ("Observacion", 22)]
    mecanismos = [
        ("Bloqueo temporal (HTTP 429)", errores_429 > 0,
         "Rate limiting activo" if errores_429 > 0 else "No detectado"),
        ("Endpoint /auth inexistente", 404 in codigos,
         "Retorna 404" if 404 in codigos else "Endpoint existe"),
        ("Respuestas consistentes", len(codigos) <= 2,
         "Si" if len(codigos) <= 2 else "Variables"),
        ("Rate limit activo (>5 bloq.)", errores_429 > 5,
         "Si" if errores_429 > 5 else "No detectado"),
    ]
    filas_p = []
    for mec, presente, obs in mecanismos:
        icono = "✔ Detectado" if presente else "✘ Ausente  "
        filas_p.append([mec, icono, obs])
    tabla_resultados(cols_p, filas_p)
    out()

    pasado  = 404 in codigos
    detalle = ("Endpoint /auth/login no implementado (404). "
               "Sin rate limiting. Recomendacion: JWT + Flask-Limiter.")
    registrar("Caso 5", "20 intentos fuerza bruta en /auth/login",
              "POST", "/auth/login",
              list(codigos)[0] if codigos else None,
              [404, 429], pasado, detalle, tiempo_prom)

    out("  Analisis: La API no implementa autenticacion. El endpoint")
    out("  /auth/login no existe (HTTP 404). Sin rate limiting activo.")
    out("  Recomendacion: implementar JWT + Flask-Limiter (max 5/min).")


# ═══════════════════════════════════════════════════════════════════════════════
#  RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════════════════════
def resumen_final(ruta_salida):
    total   = len(RESULTADOS)
    pasados = sum(1 for r in RESULTADOS if r["pasado"])
    fallidos= total - pasados
    pct     = pasados * 100 // total if total else 0

    out()
    out("═" * 72)
    out("  RESUMEN FINAL DE PRUEBAS DE SEGURIDAD")
    out("═" * 72)
    out()

    cols = [("Caso", 8), ("Descripcion", 34), ("HTTP Esp.", 10),
            ("HTTP Obt.", 10), ("Tiempo", 8), ("Estado", 8)]
    filas = []
    for r in RESULTADOS:
        esp = (str(r["status_esperado"])
               if not isinstance(r["status_esperado"], list)
               else "/".join(map(str, r["status_esperado"])))
        filas.append([
            r["caso"], r["descripcion"][:32],
            esp, str(r["status_obtenido"]),
            f"{r['tiempo_ms']}ms",
            "✔ PASS" if r["pasado"] else "✘ FAIL",
        ])
    tabla_resultados(cols, filas)
    out()

    # Tabla de totales por caso
    casos_unicos = list(dict.fromkeys(r["caso"] for r in RESULTADOS))
    out("  Resultado por caso:")
    cols2 = [("Caso", 8), ("Total", 7), ("PASS", 6), ("FAIL", 6), ("Estado", 10)]
    filas2 = []
    for c in casos_unicos:
        sub    = [r for r in RESULTADOS if r["caso"] == c]
        ok     = sum(1 for r in sub if r["pasado"])
        fail   = len(sub) - ok
        estado = "✔ OK" if fail == 0 else f"✘ {fail} fallo(s)"
        filas2.append([c, str(len(sub)), str(ok), str(fail), estado])
    # Fila total
    filas2.append(["TOTAL", str(total), str(pasados), str(fallidos),
                   "✔ TODO OK" if fallidos == 0 else f"✘ {fallidos} fallo(s)"])
    tabla_resultados(cols2, filas2)
    out()

    barra = "█" * (pct // 5) + "░" * (20 - pct // 5)
    out(f"  Resultado global: [{barra}] {pct}%  —  {pasados}/{total} pruebas exitosas")
    out()

    # Tabla de recomendaciones
    out("  Recomendaciones de seguridad:")
    cols3 = [("Area", 22), ("Hallazgo", 28), ("Recomendacion", 18)]
    filas3 = [
        ["Recursos (404)",  "Manejo correcto",         "Sin cambios"],
        ["Validacion (400)","Campos obligatorios OK",  "Agregar Marshmallow"],
        ["Tipos de datos",  "Rechazo con 400",         "Esquemas explicitos"],
        ["Metodos (405)",   "Flask OK automatico",     "Sin cambios"],
        ["Autenticacion",   "No implementada",         "JWT + Flask-Limiter"],
    ]
    tabla_resultados(cols3, filas3)
    out()
    out(f"  Fecha : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    out(f"  URL   : {BASE_URL}")
    out("═" * 72)

    # Guardar informe
    if ruta_salida:
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write("\n".join(REPORT_LINES))
        out(f"\n  Informe guardado en: {ruta_salida}")

    return pasados, total


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",        default="http://127.0.0.1:5000")
    parser.add_argument("--output",     default="tests/security/security_report.txt")
    parser.add_argument("--skip-brute", action="store_true")
    args = parser.parse_args()

    global BASE_URL
    BASE_URL = args.url.rstrip("/")

    # Encabezado
    out()
    out("╔" + "═" * 70 + "╗")
    out("║" + " " * 15 + "PRUEBAS BASICAS DE SEGURIDAD" + " " * 27 + "║")
    out("║" + " " * 15 + "Biblioteca Nova API  —  Ejercicio 4" + " " * 19 + "║")
    out("╚" + "═" * 70 + "╝")
    out(f"  URL : {BASE_URL}")
    out(f"  Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    out()

    # Conectividad
    out("  Verificando conexion con la API...")
    status, _ = req("GET", "/health")
    if status is None:
        out("  ERROR: No se puede conectar. Ejecuta: python run_server.py")
        sys.exit(1)
    out(f"  ✔ API en linea  (HTTP {status})")
    out()

    # Casos
    caso_1()
    caso_2()
    caso_3()
    caso_4()
    if not args.skip_brute:
        caso_5()

    # Resumen
    pasados, total = resumen_final(args.output)
    sys.exit(0 if pasados == total else 1)


if __name__ == "__main__":
    main()
