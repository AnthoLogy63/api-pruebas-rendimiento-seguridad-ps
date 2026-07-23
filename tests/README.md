# Pruebas de rendimiento — Biblioteca Nova

Este directorio contiene scripts para pruebas de carga con **K6** y **Apache JMeter**.

## Requisitos previos

1. API en ejecución: `python app.py`
2. Datos de prueba cargados: `python seed.py --reset`
3. URL base: `http://localhost:5000`

---

## K6

### Instalación

```bash
# Windows (Chocolatey)
choco install k6

# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

### Ejecutar prueba de carga

Desde la raíz del proyecto:

```bash
k6 run tests/k6/load_test.js
```

Con URL personalizada:

```bash
k6 run -e BASE_URL=http://192.168.1.63:5000 tests/k6/load_test.js
```

### Endpoints probados por K6

| Endpoint | Método |
|----------|--------|
| `/health` | GET |
| `/libros` | GET |
| `/libros/estadisticas` | GET |
| `/libros/buscar?categoria=Novela` | GET |
| `/libros/1` | GET |
| `/libros` | POST |
| `/prestamos/activos` | GET |
| `/prestamos/estadisticas` | GET |

Los resultados se guardan en `tests/k6/results/summary.json`.

---

## Apache JMeter

### Instalación

Descargar desde: https://jmeter.apache.org/download_jmeter.cgi

### Plan de prueba incluido

Abrir en JMeter: `tests/jmeter/biblioteca_nova.jmx`

### Configuración recomendada

1. **Thread Group**: 25 usuarios, ramp-up 30s, loop 5
2. **HTTP Request Defaults**: Server = `localhost`, Port = `5000`
3. Ejecutar después de `python seed.py --reset`

### Endpoints en el plan JMeter

- GET `/health`
- GET `/libros`
- GET `/libros/estadisticas`
- GET `/libros/buscar?autor=García`
- GET `/prestamos/activos`
- GET `/prestamos/estadisticas`
- POST `/libros` (con CSV de datos)
- GET `/libros/${id}`

### CSV de datos para JMeter

Usar `tests/jmeter/libros_data.csv` para peticiones POST variables.

---

## Consejos para pruebas de rendimiento

- Ejecutar la API **sin debug** para resultados más realistas:

```bash
python run_server.py
```

- Usar `seed.py --reset` antes de cada sesión de pruebas para datos consistentes.
- Monitorear tiempos p95; el script K6 falla si p95 > 500ms o error rate > 10%.
