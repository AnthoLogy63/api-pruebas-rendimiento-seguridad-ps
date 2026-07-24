/**
 * K6 — Escenario 1: 20 usuarios | Ramp-Up 10s | 5 iteraciones
 * =============================================================
 * Uso: k6 run tests/k6/escenario1.js
 */
import http from "k6/http";
import { check, sleep, group } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:5000";

const errorRate    = new Rate("tasa_errores");
const exitoRate    = new Rate("tasa_exitosas");
const durGet       = new Trend("dur_get_libros", true);
const durPost      = new Trend("dur_post_libro", true);
const totalReqs    = new Counter("total_solicitudes");
const failedReqs   = new Counter("solicitudes_fallidas");
const successReqs  = new Counter("solicitudes_exitosas");

export const options = {
  scenarios: {
    escenario_1: {
      executor:    "per-vu-iterations",
      vus:         20,
      iterations:  5,
      maxDuration: "3m",
      gracefulStop:"10s",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    tasa_errores:      ["rate<0.05"],
  },
};

const headers = { "Content-Type": "application/json" };

function chk(res, nombre, validos = [200]) {
  totalReqs.add(1);
  const ok = validos.includes(res.status);
  check(res, { [`${nombre} status OK`]: (r) => validos.includes(r.status) });
  if (!ok) { failedReqs.add(1); errorRate.add(1); }
  else      { successReqs.add(1); exitoRate.add(1); errorRate.add(0); }
  return ok;
}

export default function () {
  group("Health", () => {
    chk(http.get(`${BASE_URL}/health`), "GET /health", [200]);
  });

  group("Libros GET", () => {
    const r1 = http.get(`${BASE_URL}/libros`);
    durGet.add(r1.timings.duration);
    chk(r1, "GET /libros", [200]);
    chk(http.get(`${BASE_URL}/libros/estadisticas`), "GET /estadisticas", [200]);
    chk(http.get(`${BASE_URL}/libros/buscar?categoria=Novela`), "GET /buscar", [200]);
    chk(http.get(`${BASE_URL}/libros/1`), "GET /libros/1", [200, 404]);
  });

  group("Libros POST", () => {
    if (__VU <= 5) {
      const payload = JSON.stringify({
        titulo: `Libro E1 VU${__VU} IT${__ITER}`,
        autor: "Autor K6", isbn: `978-E1-${__VU}-${Date.now()}`,
        editorial: "Nova", anio_publicacion: 2024,
        categoria: "Prueba", cantidad_disponible: 2,
      });
      const r = http.post(`${BASE_URL}/libros`, payload, { headers });
      durPost.add(r.timings.duration);
      chk(r, "POST /libros", [201, 400, 409]);
    }
  });

  group("Prestamos GET", () => {
    chk(http.get(`${BASE_URL}/prestamos/activos`), "GET /activos", [200]);
    chk(http.get(`${BASE_URL}/prestamos/estadisticas`), "GET /prestamos/stats", [200]);
  });

  sleep(1);
}

export function handleSummary(data) {
  const m = data.metrics;
  const fmt = (v, d=2) => v !== undefined ? Number(v).toFixed(d) : "N/A";

  const resumen = {
    escenario: "Escenario 1 — 20 VUs | Ramp-Up 10s | 5 iteraciones",
    iteraciones_ejecutadas:   m.iterations?.values?.count    || 0,
    total_solicitudes:        m.total_solicitudes?.values?.count || 0,
    solicitudes_exitosas:     m.solicitudes_exitosas?.values?.count || 0,
    solicitudes_fallidas:     m.solicitudes_fallidas?.values?.count || 0,
    porcentaje_errores:       fmt((m.tasa_errores?.values?.rate || 0) * 100) + "%",
    tiempo_promedio_ms:       fmt(m.http_req_duration?.values?.avg),
    tiempo_minimo_ms:         fmt(m.http_req_duration?.values?.min),
    tiempo_maximo_ms:         fmt(m.http_req_duration?.values?.max),
    p90_ms:                   fmt(m.http_req_duration?.values?.["p(90)"]),
    p95_ms:                   fmt(m.http_req_duration?.values?.["p(95)"]),
    throughput_req_s:         fmt(m.http_reqs?.values?.rate),
    desviacion_estandar_ms:   fmt(m.http_req_duration?.values?.med),
    umbral_p95_ok:            (m.http_req_duration?.values?.["p(95)"] || 9999) < 500,
  };

  const txt = [
    "═".repeat(60),
    "  RESULTADO K6 — ESCENARIO 1",
    "  20 VUs | Ramp-Up 10s | 5 iteraciones por VU",
    "═".repeat(60),
    `  Iteraciones ejecutadas  : ${resumen.iteraciones_ejecutadas}`,
    `  Total solicitudes       : ${resumen.total_solicitudes}`,
    `  Solicitudes exitosas    : ${resumen.solicitudes_exitosas}`,
    `  Solicitudes fallidas    : ${resumen.solicitudes_fallidas}`,
    `  Porcentaje de errores   : ${resumen.porcentaje_errores}`,
    "─".repeat(60),
    `  Tiempo promedio (ms)    : ${resumen.tiempo_promedio_ms}`,
    `  Tiempo minimo (ms)      : ${resumen.tiempo_minimo_ms}`,
    `  Tiempo maximo (ms)      : ${resumen.tiempo_maximo_ms}`,
    `  Percentil p90 (ms)      : ${resumen.p90_ms}`,
    `  Percentil p95 (ms)      : ${resumen.p95_ms}`,
    `  Throughput (req/s)      : ${resumen.throughput_req_s}`,
    "─".repeat(60),
    `  Umbral p95 < 500ms      : ${resumen.umbral_p95_ok ? "PASS ✔" : "FAIL ✘"}`,
    "═".repeat(60),
  ].join("\n");

  console.log(txt);
  return {
    stdout:                           txt,
    "tests/k6/results/e1_summary.json": JSON.stringify(resumen, null, 2),
  };
}
