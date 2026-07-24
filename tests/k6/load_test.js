/**
 * Script de pruebas de carga K6 — Biblioteca Nova API
 * =====================================================
 * Ejercicio 3: Pruebas de Rendimiento con K6
 *
 * Escenarios:
 *   - Escenario 1: 20 VUs | Ramp-Up 10s | 5 iteraciones por VU
 *   - Escenario 2: 50 VUs | Ramp-Up 20s | 10 iteraciones por VU
 *   - Escenario 3: 100 VUs | Ramp-Up 30s | 15 iteraciones por VU
 *
 * Ejecución:
 *   k6 run tests/k6/load_test.js
 *   k6 run -e BASE_URL=http://192.168.1.x:5000 tests/k6/load_test.js
 *   k6 run -e SCENARIO=escenario_2 tests/k6/load_test.js   (solo un escenario)
 */

import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// ── Configuración base ────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:5000";

// ── Métricas personalizadas ───────────────────────────────────────────────────
const errorRate       = new Rate("tasa_errores");
const successRate     = new Rate("tasa_exitosas");
const duracionGet     = new Trend("duracion_get_libros",    true);
const duracionPost    = new Trend("duracion_post_libro",    true);
const duracionPrestam = new Trend("duracion_get_prestamos", true);
const totalRequests   = new Counter("total_solicitudes");
const failedRequests  = new Counter("solicitudes_fallidas");

// ── Opciones: 3 escenarios del enunciado ─────────────────────────────────────
export const options = {
  scenarios: {
    // ── Escenario 1: 20 usuarios | Ramp-Up 10s | 5 iteraciones ──────────────
    escenario_1: {
      executor:           "per-vu-iterations",
      vus:                20,
      iterations:         5,
      maxDuration:        "3m",
      startTime:          "0s",
      gracefulStop:       "10s",
      tags:               { escenario: "E1_20VUs" },
      env:                { RAMP_UP: "10" },
    },

    // ── Escenario 2: 50 usuarios | Ramp-Up 20s | 10 iteraciones ─────────────
    escenario_2: {
      executor:           "per-vu-iterations",
      vus:                50,
      iterations:         10,
      maxDuration:        "6m",
      startTime:          "4m",          // inicia después del Escenario 1
      gracefulStop:       "20s",
      tags:               { escenario: "E2_50VUs" },
      env:                { RAMP_UP: "20" },
    },

    // ── Escenario 3: 100 usuarios | Ramp-Up 30s | 15 iteraciones ────────────
    escenario_3: {
      executor:           "per-vu-iterations",
      vus:                100,
      iterations:         15,
      maxDuration:        "12m",
      startTime:          "12m",         // inicia después del Escenario 2
      gracefulStop:       "30s",
      tags:               { escenario: "E3_100VUs" },
      env:                { RAMP_UP: "30" },
    },
  },

  // ── Umbrales de calidad ──────────────────────────────────────────────────
  thresholds: {
    // 95% de las solicitudes deben completarse en menos de 500ms
    http_req_duration:    ["p(95)<500", "p(99)<1000"],
    // La tasa de errores debe ser menor al 5%
    tasa_errores:         ["rate<0.05"],
    // Al menos el 95% deben ser exitosas
    tasa_exitosas:        ["rate>0.95"],
    // Tiempo de duración GET libros (p95 < 400ms)
    duracion_get_libros:  ["p(95)<400"],
    // Tiempo de duración POST libro (p95 < 600ms)
    duracion_post_libro:  ["p(95)<600"],
  },
};

// ── Headers comunes ──────────────────────────────────────────────────────────
const jsonHeaders = { "Content-Type": "application/json" };

// ── Función auxiliar: verificar respuesta ────────────────────────────────────
function verificar(res, nombre, codigosValidos = [200]) {
  totalRequests.add(1);
  const ok = codigosValidos.includes(res.status);

  check(res, {
    [`${nombre} - código válido`]:        (r) => codigosValidos.includes(r.status),
    [`${nombre} - sin timeout`]:          (r) => r.timings.duration < 5000,
    [`${nombre} - respuesta no vacía`]:   (r) => r.body && r.body.length > 0,
  });

  if (!ok) {
    failedRequests.add(1);
    errorRate.add(1);
  } else {
    successRate.add(1);
    errorRate.add(0);
  }

  return ok;
}

// ── Función principal (ejecutada por cada VU en cada iteración) ──────────────
export default function () {
  const tag = { escenario: __ENV.SCENARIO_TAG || "general" };

  // ── GRUPO 1: Health check ─────────────────────────────────────────────────
  group("Health & Estado", () => {
    let res = http.get(`${BASE_URL}/health`, { tags: tag });
    verificar(res, "GET /health", [200]);

    res = http.get(`${BASE_URL}/biblioteca/estado`, { tags: tag });
    verificar(res, "GET /biblioteca/estado", [200]);
  });

  // ── GRUPO 2: Consultas de Libros ─────────────────────────────────────────
  group("Consultas Libros", () => {
    // Listar todos los libros
    let res = http.get(`${BASE_URL}/libros`, { tags: tag });
    duracionGet.add(res.timings.duration);
    verificar(res, "GET /libros", [200]);

    // Estadísticas
    res = http.get(`${BASE_URL}/libros/estadisticas`, { tags: tag });
    verificar(res, "GET /libros/estadisticas", [200]);

    // Buscar por categoría
    res = http.get(`${BASE_URL}/libros/buscar?categoria=Novela`, { tags: tag });
    verificar(res, "GET /libros/buscar?categoria=Novela", [200]);

    // Buscar por autor
    res = http.get(`${BASE_URL}/libros/buscar?autor=Garc%C3%ADa`, { tags: tag });
    verificar(res, "GET /libros/buscar?autor=García", [200]);

    // Categorías disponibles
    res = http.get(`${BASE_URL}/libros/categorias`, { tags: tag });
    verificar(res, "GET /libros/categorias", [200]);

    // Obtener libro por ID (puede no existir)
    res = http.get(`${BASE_URL}/libros/1`, { tags: tag });
    verificar(res, "GET /libros/1", [200, 404]);
  });

  // ── GRUPO 3: Operaciones CRUD de Libros ──────────────────────────────────
  group("CRUD Libros", () => {
    // Solo los primeros 5 VUs crean libros para no saturar el ISBN único
    if (__VU <= 5) {
      const timestamp = Date.now();
      const payload = JSON.stringify({
        titulo:               `Libro Prueba K6 VU${__VU} IT${__ITER}`,
        autor:                "Autor de Prueba K6",
        isbn:                 `978-K6-${__VU}-${timestamp}`,
        editorial:            "Editorial Nova",
        anio_publicacion:     2024,
        categoria:            "Prueba",
        cantidad_disponible:  3,
      });

      let res = http.post(`${BASE_URL}/libros`, payload, {
        headers: jsonHeaders,
        tags:    tag,
      });
      duracionPost.add(res.timings.duration);
      const ok = verificar(res, "POST /libros", [201, 400, 409]);

      // Si se creó el libro, intentar actualizar y luego eliminar
      if (res.status === 201) {
        let body;
        try { body = JSON.parse(res.body); } catch (e) { body = null; }

        if (body && body.data && body.data.id) {
          const libroId = body.data.id;

          // PUT — Actualizar cantidad
          const updatePayload = JSON.stringify({
            titulo:               `Libro Prueba K6 VU${__VU} IT${__ITER} (actualizado)`,
            autor:                "Autor de Prueba K6",
            isbn:                 `978-K6-${__VU}-${timestamp}`,
            editorial:            "Editorial Nova",
            anio_publicacion:     2024,
            categoria:            "Prueba",
            cantidad_disponible:  5,
          });
          res = http.put(`${BASE_URL}/libros/${libroId}`, updatePayload, {
            headers: jsonHeaders,
            tags:    tag,
          });
          verificar(res, "PUT /libros/:id", [200, 400, 404]);

          // DELETE — Eliminar libro creado
          res = http.del(`${BASE_URL}/libros/${libroId}`, null, { tags: tag });
          verificar(res, "DELETE /libros/:id", [200, 404, 409]);
        }
      }
    }
  });

  // ── GRUPO 4: Consultas de Préstamos ──────────────────────────────────────
  group("Consultas Prestamos", () => {
    let res = http.get(`${BASE_URL}/prestamos/activos`, { tags: tag });
    duracionPrestam.add(res.timings.duration);
    verificar(res, "GET /prestamos/activos", [200]);

    res = http.get(`${BASE_URL}/prestamos/estadisticas`, { tags: tag });
    verificar(res, "GET /prestamos/estadisticas", [200]);

    res = http.get(`${BASE_URL}/prestamos`, { tags: tag });
    verificar(res, "GET /prestamos", [200]);
  });

  // Pequeña pausa entre iteraciones para simular comportamiento real
  sleep(1);
}

// ── Resumen final personalizado ───────────────────────────────────────────────
export function handleSummary(data) {
  const metrics = data.metrics;

  const fmt = (v, dec = 2) => (v !== undefined ? Number(v).toFixed(dec) : "N/A");

  const resumen = {
    timestamp:          new Date().toISOString(),
    escenarios: {
      escenario_1:      { vus: 20, ramp_up: "10s", iteraciones: 5  },
      escenario_2:      { vus: 50, ramp_up: "20s", iteraciones: 10 },
      escenario_3:      { vus: 100, ramp_up: "30s", iteraciones: 15 },
    },
    metricas_globales: {
      total_solicitudes:            metrics.total_solicitudes?.values?.count      || 0,
      solicitudes_exitosas:         metrics.tasa_exitosas?.values?.passes          || 0,
      solicitudes_fallidas:         metrics.solicitudes_fallidas?.values?.count    || 0,
      porcentaje_errores:           fmt((metrics.tasa_errores?.values?.rate || 0) * 100) + "%",
      tiempo_promedio_ms:           fmt(metrics.http_req_duration?.values?.avg),
      tiempo_minimo_ms:             fmt(metrics.http_req_duration?.values?.min),
      tiempo_maximo_ms:             fmt(metrics.http_req_duration?.values?.max),
      p90_ms:                       fmt(metrics.http_req_duration?.values?.["p(90)"]),
      p95_ms:                       fmt(metrics.http_req_duration?.values?.["p(95)"]),
      p99_ms:                       fmt(metrics.http_req_duration?.values?.["p(99)"]),
      desviacion_estandar_ms:       fmt(metrics.http_req_duration?.values?.["med"]),
      throughput_req_por_seg:       fmt(metrics.http_reqs?.values?.rate),
      iteraciones_totales:          metrics.iterations?.values?.count             || 0,
    },
    thresholds_resultado: data.state?.testRunDurationMs ? "COMPLETADO" : "PARCIAL",
  };

  const reporteTexto = `
╔══════════════════════════════════════════════════════════════╗
║          INFORME DE PRUEBAS K6 — BIBLIOTECA NOVA             ║
╠══════════════════════════════════════════════════════════════╣
║  Fecha: ${resumen.timestamp.split("T")[0]}                                           ║
╠══════════════════════════════════════════════════════════════╣
║  CONFIGURACIÓN DE ESCENARIOS                                 ║
║  E1: 20 VUs | Ramp-Up 10s | 5 iteraciones                   ║
║  E2: 50 VUs | Ramp-Up 20s | 10 iteraciones                  ║
║  E3: 100 VUs | Ramp-Up 30s | 15 iteraciones                 ║
╠══════════════════════════════════════════════════════════════╣
║  MÉTRICAS GLOBALES                                           ║
║  Total solicitudes   : ${String(resumen.metricas_globales.total_solicitudes).padEnd(35)}║
║  Solicitudes fallidas: ${String(resumen.metricas_globales.solicitudes_fallidas).padEnd(35)}║
║  % Errores           : ${String(resumen.metricas_globales.porcentaje_errores).padEnd(35)}║
║  Tiempo promedio     : ${String(resumen.metricas_globales.tiempo_promedio_ms + " ms").padEnd(35)}║
║  Tiempo mínimo       : ${String(resumen.metricas_globales.tiempo_minimo_ms + " ms").padEnd(35)}║
║  Tiempo máximo       : ${String(resumen.metricas_globales.tiempo_maximo_ms + " ms").padEnd(35)}║
║  p90                 : ${String(resumen.metricas_globales.p90_ms + " ms").padEnd(35)}║
║  p95                 : ${String(resumen.metricas_globales.p95_ms + " ms").padEnd(35)}║
║  p99                 : ${String(resumen.metricas_globales.p99_ms + " ms").padEnd(35)}║
║  Throughput          : ${String(resumen.metricas_globales.throughput_req_por_seg + " req/s").padEnd(35)}║
║  Iteraciones totales : ${String(resumen.metricas_globales.iteraciones_totales).padEnd(35)}║
╚══════════════════════════════════════════════════════════════╝
`;

  console.log(reporteTexto);

  return {
    stdout:                                    reporteTexto,
    "tests/k6/results/summary.json":           JSON.stringify(resumen, null, 2),
    "tests/k6/results/raw_summary.json":       JSON.stringify(data,    null, 2),
  };
}
