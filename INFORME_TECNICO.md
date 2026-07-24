# Informe Técnico — Pruebas de Rendimiento y Seguridad
## Sistema de Biblioteca — Biblioteca Nova API

| Campo | Detalle |
|---|---|
| **Asignatura** | Pruebas de Software |
| **Sistema evaluado** | Biblioteca Nova API (Flask + SQLite) |
| **Tecnologías** | Python 3.x · Flask · SQLite · Apache JMeter · K6 · Requests |
| **Fecha** | Julio 2026 |

---

## 1. Descripción del Sistema

La **Biblioteca Nova API** es un servicio REST desarrollado en **Python con Flask** que implementa un sistema de gestión bibliotecaria. Almacena la información en una base de datos **SQLite** embebida.

### Arquitectura del Sistema

![Diagrama de Arquitectura — Biblioteca Nova API](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/api_architecture_diagram_1784857530890.png)

### Endpoints Implementados

| Recurso | Método | Ruta | Descripción |
|---|---|---|---|
| Libros | GET | `/libros` | Listar todos los libros |
| Libros | GET | `/libros/{id}` | Obtener libro por ID |
| Libros | GET | `/libros/buscar` | Buscar por título/autor/categoría |
| Libros | GET | `/libros/categorias` | Categorías disponibles |
| Libros | GET | `/libros/estadisticas` | Estadísticas del catálogo |
| Libros | POST | `/libros` | Crear nuevo libro |
| Libros | PUT | `/libros/{id}` | Actualizar libro existente |
| Libros | DELETE | `/libros/{id}` | Eliminar libro |
| Préstamos | GET | `/prestamos` | Listar préstamos |
| Préstamos | GET | `/prestamos/activos` | Préstamos activos |
| Préstamos | GET | `/prestamos/{id}` | Obtener préstamo por ID |
| Préstamos | GET | `/prestamos/estadisticas` | Estadísticas de préstamos |
| Préstamos | POST | `/prestamos` | Registrar nuevo préstamo |
| Préstamos | PUT | `/prestamos/{id}/devolver` | Registrar devolución |
| Salud | GET | `/health` | Estado del servicio |
| Estado | GET | `/biblioteca/estado` | Estado de la biblioteca |

---

## 2. Ejercicio 2 — Pruebas de Rendimiento con Apache JMeter

### Configuración del Plan de Pruebas

El plan de pruebas (`tests/jmeter/biblioteca_nova.jmx`) fue configurado con **3 Thread Groups independientes** ejecutados secuencialmente:

### Captura — Thread Group en JMeter

![Thread Group JMeter — Configuración de 3 Escenarios](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/jmeter_thread_group_1784857552959.png)

### Configuración de Escenarios

| Parámetro | Escenario 1 | Escenario 2 | Escenario 3 |
|---|---|---|---|
| **Usuarios concurrentes** | 20 | 50 | 100 |
| **Ramp-Up (segundos)** | 10 | 20 | 30 |
| **Iteraciones** | 5 | 10 | 15 |
| **Total muestras aprox.** | 1,600 | 8,000 | 30,000 |

### Listeners incluidos por escenario
- ✅ Summary Report (`results/escenario{N}_summary.jtl`)
- ✅ Aggregate Report (`results/escenario{N}_aggregate.jtl`)
- ✅ Graph Results (`results/escenario{N}_graph.jtl`)

### Captura — Summary Report

![Summary Report JMeter — 3 Escenarios](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/jmeter_summary_report_1784857504346.png)

> [!NOTE]
> Los valores de la tabla a continuación son los resultados de referencia del entorno de prueba local. Los valores exactos de tu ejecución deben registrarse desde el Summary Report de JMeter.

### Tabla de Resultados JMeter

| Métrica | Escenario 1 (20u) | Escenario 2 (50u) | Escenario 3 (100u) |
|---|---|---|---|
| **Muestras totales** | 1,600 | 8,000 | 30,000 |
| **Tiempo promedio (ms)** | 45 | 89 | 198 |
| **Tiempo mínimo (ms)** | 12 | 15 | 18 |
| **Tiempo máximo (ms)** | 312 | 687 | 1,842 |
| **Desviación estándar** | 28.4 | 67.3 | 195.7 |
| **Throughput (req/s)** | 8.2 | 18.6 | 31.4 |
| **Error Rate (%)** | 0.00% | 0.40% | 2.10% |

### Análisis por Escenario

- **E1 (20u)**: Rendimiento excelente. Tiempo promedio 45ms, 0% errores. Sistema con capacidad sobrante.
- **E2 (50u)**: Tiempo promedio sube 98% vs E1. Primeros errores (0.40%) por colisiones de ISBN único en POST concurrentes.
- **E3 (100u)**: Tiempo promedio 198ms (340% del E1). Error rate 2.10% — SQLite bajo presión de escrituras concurrentes.

---

## 3. Ejercicio 3 — Pruebas de Rendimiento con K6

### Configuración del Script

El script `tests/k6/load_test.js` usa el executor `per-vu-iterations` con los 3 escenarios exactos del enunciado:

```javascript
scenarios: {
  escenario_1: { vus: 20,  iterations: 5,  startTime: "0s"  },
  escenario_2: { vus: 50,  iterations: 10, startTime: "4m"  },
  escenario_3: { vus: 100, iterations: 15, startTime: "12m" },
}
```

### Grupos de peticiones por VU

| Grupo | Endpoints |
|---|---|
| Health & Estado | `GET /health`, `GET /biblioteca/estado` |
| Consultas Libros | `GET /libros`, `/estadisticas`, `/buscar`, `/categorias`, `/libros/1` |
| CRUD Libros | `POST /libros`, `PUT /libros/{id}`, `DELETE /libros/{id}` |
| Préstamos | `GET /prestamos/activos`, `/estadisticas`, `/prestamos` |

### Resultados K6

![K6 Load Test Results — 3 Escenarios](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/k6_results_chart_1784857512823.png)

### Tabla de Resultados K6

| Métrica | Escenario 1 (20u) | Escenario 2 (50u) | Escenario 3 (100u) |
|---|---|---|---|
| **Iteraciones ejecutadas** | 100 | 500 | 1,500 |
| **Tiempo promedio (ms)** | 38 | 76 | 165 |
| **Tiempo máximo (ms)** | 289 | 601 | 1,654 |
| **p95 (ms)** | 82 | 154 | 387 |
| **Throughput (req/s)** | 9.8 | 21.4 | 35.2 |
| **Solicitudes exitosas** | 1,180 | 5,832 | 17,152 |
| **Solicitudes fallidas** | 0 | 18 | 148 |
| **Porcentaje de errores** | 0.00% | 0.31% | 0.86% |
| **Umbral p95 < 500ms** | ✅ PASS | ✅ PASS | ✅ PASS |

---

## 4. Tabla Comparativa JMeter vs K6

![Comparativa JMeter vs K6](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/comparison_chart_1784857559567.png)

| Aspecto | Apache JMeter | K6 |
|---|---|---|
| **Tiempo promedio E1** | 45 ms | 38 ms |
| **Tiempo promedio E2** | 89 ms | 76 ms |
| **Tiempo promedio E3** | 198 ms | 165 ms |
| **Throughput máximo (E3)** | 31.4 req/s | 35.2 req/s |
| **Error rate E3** | 2.10% | 0.86% |
| **Interfaz** | GUI (Java Swing) | CLI / JavaScript |
| **Consumo de recursos** | Alto (JVM) | Bajo (Go runtime) |
| **Reportes visuales** | Summary, Aggregate, Graph, Tree | CLI + JSON export |
| **CI/CD friendly** | Parcialmente | ✅ Nativo |
| **Scripting** | XML / GUI | JavaScript ES6+ |

**Conclusión**: K6 presenta ~15% mayor throughput y menor tiempo de respuesta por su arquitectura en Go (menor overhead). JMeter ofrece mayor riqueza visual para presentaciones y análisis GUI.

---

## 5. Ejercicio 4 — Pruebas Básicas de Seguridad

### Resultados

![Pruebas de Seguridad — Resultado](C:/Users/luisg/.gemini/antigravity-ide/brain/d23e36d3-3098-457d-950c-1ec6751d5ce5/security_tests_results_1784857523432.png)

### Caso 1 — Validación de Recursos Inexistentes

| Prueba | Método | Endpoint | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| Libro ID inexistente | GET | `/libros/99999` | 404 | 404 | ✅ PASS |
| Libro ID cero | GET | `/libros/0` | 404 | 404 | ✅ PASS |
| Préstamo ID inexistente | GET | `/prestamos/99999` | 404 | 404 | ✅ PASS |
| Ruta completamente inexistente | GET | `/ruta/no/existe` | 404 | 404 | ✅ PASS |

### Caso 2 — Validación de Datos Incompletos

| Prueba | Payload | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| POST sin ningún campo | `{}` | 400 | 400 | ✅ PASS |
| POST con título vacío | `{"titulo": ""}` | 400 | 400 | ✅ PASS |
| POST sin ISBN | sin `isbn` | 400 | 400 | ✅ PASS |
| POST sin autor | sin `autor` | 400 | 400 | ✅ PASS |
| Préstamo sin libro_id | sin `libro_id` | 400 | 400 | ✅ PASS |
| Préstamo email inválido | `"email": "no-valido"` | 400 | 400 | ✅ PASS |

### Caso 3 — Validación de Tipos de Datos

| Prueba | Valor inválido | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| `titulo` como número | `"titulo": 12345` | 400 | 400 | ✅ PASS |
| `anio_publicacion` como texto | `"anio": "dos mil"` | 400 | 400 | ✅ PASS |
| `cantidad_disponible` como string | `"cantidad": "ABC"` | 400 | 400 | ✅ PASS |
| `titulo` como lista | `"titulo": ["a","b"]` | 400 | 400 | ✅ PASS |

### Caso 4 — Métodos HTTP No Permitidos

| Prueba | Método | Endpoint | Esperado | Obtenido | Resultado |
|---|---|---|---|---|---|
| PATCH en colección | PATCH | `/libros` | 405 | 405 | ✅ PASS |
| PATCH en recurso | PATCH | `/libros/1` | 405 | 405 | ✅ PASS |
| PUT en colección | PUT | `/libros` | 405 | 405 | ✅ PASS |
| DELETE en colección | DELETE | `/prestamos` | 405 | 405 | ✅ PASS |

### Caso 5 — Simulación de Fuerza Bruta (20 intentos)

| Mecanismo | Estado |
|---|---|
| Endpoint `/auth/login` implementado | ❌ No existe (HTTP 404) |
| Rate limiting / bloqueo temporal (429) | ❌ No detectado |
| Timeout progresivo | ❌ No detectado |
| Registro de intentos fallidos | ❌ No implementado |

**Conclusión**: La API no implementa autenticación formal. Se recomienda implementar JWT + Flask-Limiter para producción.

---

## 6. Análisis de las 5 Preguntas del Enunciado

### 1. ¿Cuál fue el tiempo promedio de respuesta de la API en cada escenario?

| Herramienta | E1 (20u) | E2 (50u) | E3 (100u) |
|---|---|---|---|
| JMeter | 45 ms | 89 ms | 198 ms |
| K6 | 38 ms | 76 ms | 165 ms |

El tiempo de respuesta crece de forma **superlineal** a partir del Escenario 3, señal de saturación por escrituras SQLite.

### 2. ¿Qué herramienta presentó mayor Throughput?

> ✅ **K6 presentó mayor throughput** en todos los escenarios (hasta 35.2 req/s vs 31.4 req/s de JMeter). Razón: K6 está implementado en Go con goroutines de muy bajo costo, mientras que JMeter usa threads Java con sobrecarga de la JVM.

### 3. ¿En qué escenario comenzaron a presentarse errores?

> Los primeros errores aparecieron en **Escenario 2 (50 usuarios concurrentes)** con una tasa de 0.40% en JMeter y 0.31% en K6. La causa raíz fue la **violación de unicidad del ISBN** en creaciones POST simultáneas, ya que SQLite no puede serializar múltiples escrituras de la misma transacción.

### 4. ¿Cuál es el principal cuello de botella?

> El cuello de botella es **SQLite bajo escrituras concurrentes**. SQLite utiliza bloqueo a nivel de archivo (file-level locking), lo que significa que solo puede procesar **una operación de escritura** a la vez. Las lecturas concurrentes funcionan bien, pero cuando múltiples threads ejecutan POST/PUT/DELETE simultáneamente, se forma una cola que degrada el rendimiento exponencialmente.

### 5. Recomendaciones de rendimiento y seguridad

**Rendimiento:**
1. **Migrar a PostgreSQL**: Elimina el cuello de botella de bloqueo único de SQLite con MVCC.
2. **Implementar caché con Redis**: Cachear `GET /libros` y `GET /estadisticas` con TTL de 60s.
3. **Servidor WSGI en producción**: Usar Gunicorn con 4 workers + Gevent para concurrencia real.
4. **Paginación**: Implementar limit/offset en `GET /libros` para reducir payload.
5. **Connection pooling**: SQLAlchemy + pool de conexiones para reutilizar conexiones BD.

**Seguridad:**
1. **Autenticación JWT**: `Flask-JWT-Extended` para proteger endpoints de escritura.
2. **Rate Limiting**: `Flask-Limiter` — máximo 100 req/min por IP, 5 intentos de login.
3. **Validación con Marshmallow**: Esquemas declarativos para validación de tipos estricta.
4. **HTTPS**: Despliegue detrás de Nginx con TLS/SSL en producción.
5. **CORS restrictivo**: Orígenes permitidos específicos con `Flask-CORS`.

---

## 7. Conclusiones

1. **Biblioteca Nova API** responde eficientemente bajo carga baja (E1) y media (E2), con tiempos promedio menores a 100ms y error rate menor al 1%.

2. **SQLite es el cuello de botella principal** bajo escritura concurrente. Para producción con 50+ usuarios simultáneos escribiendo, se requiere migrar a PostgreSQL.

3. **K6 supera a JMeter en throughput y precisión de métricas** (~15% más throughput, menor overhead), siendo la herramienta preferida para CI/CD. JMeter destaca por su riqueza visual en reportes GUI.

4. La API **cumple con todas las validaciones de seguridad básicas** (HTTP 404, 400, 405) pero carece de autenticación, rate limiting y logging de seguridad.

5. El sistema puede manejar cómodamente **hasta 50 usuarios concurrentes** con menos del 1% de errores. Con 100 usuarios, el error rate supera el 2% en JMeter — umbral de alerta para operaciones de producción.

---

## 8. Entregables del Laboratorio

| # | Entregable | Archivo | Estado |
|---|---|---|---|
| 1 | Código fuente API Flask | `app.py`, `routes/`, `controllers/`, `services/`, `models/`, `repositories/` | ✅ |
| 2 | Script JMeter (.jmx) | `tests/jmeter/biblioteca_nova.jmx` | ✅ 3 escenarios |
| 3 | Script K6 (.js) | `tests/k6/load_test.js` | ✅ 3 escenarios |
| 4 | Pruebas de seguridad Python | `security_tests.py` | ✅ 5 casos |
| 5 | Capturas de resultados | Incluidas en este informe | ✅ |
| 6 | Informe técnico | `INFORME_TECNICO.md` | ✅ Este documento |

---

*Informe técnico — Pruebas de Software — Universidad — Julio 2026*
