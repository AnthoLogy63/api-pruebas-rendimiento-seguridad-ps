import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:5000";

const errorRate = new Rate("errors");
const listLibrosDuration = new Trend("list_libros_duration");
const createLibroDuration = new Trend("create_libro_duration");
const listPrestamosDuration = new Trend("list_prestamos_duration");

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 25 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    errors: ["rate<0.1"],
  },
};

const libroPayload = {
  titulo: "Libro de prueba K6",
  autor: "Autor K6",
  isbn: `978-K6-${__VU}-${__ITER}`,
  editorial: "Nova Press",
  anio_publicacion: 2024,
  categoria: "Prueba",
  cantidad_disponible: 2,
};

export default function () {
  // Health check
  let res = http.get(`${BASE_URL}/health`);
  check(res, { "health status 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Listar libros
  res = http.get(`${BASE_URL}/libros`);
  listLibrosDuration.add(res.timings.duration);
  check(res, { "list libros 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Estadísticas
  res = http.get(`${BASE_URL}/libros/estadisticas`);
  check(res, { "stats libros 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Buscar libros
  res = http.get(`${BASE_URL}/libros/buscar?categoria=Novela`);
  check(res, { "buscar libros 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Listar préstamos activos
  res = http.get(`${BASE_URL}/prestamos/activos`);
  listPrestamosDuration.add(res.timings.duration);
  check(res, { "list prestamos 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Estadísticas préstamos
  res = http.get(`${BASE_URL}/prestamos/estadisticas`);
  check(res, { "stats prestamos 200": (r) => r.status === 200 }) || errorRate.add(1);

  // Crear libro (solo algunos VUs para no saturar ISBN)
  if (__VU <= 3) {
    const payload = { ...libroPayload, isbn: `978-K6-${__VU}-${Date.now()}-${__ITER}` };
    res = http.post(`${BASE_URL}/libros`, JSON.stringify(payload), {
      headers: { "Content-Type": "application/json" },
    });
    createLibroDuration.add(res.timings.duration);
    check(res, { "create libro 201": (r) => r.status === 201 }) || errorRate.add(1);
  }

  // Obtener libro por ID
  res = http.get(`${BASE_URL}/libros/1`);
  check(res, { "get libro 200 or 404": (r) => r.status === 200 || r.status === 404 }) ||
    errorRate.add(1);

  sleep(1);
}

export function handleSummary(data) {
  return {
    stdout: JSON.stringify(data, null, 2),
    "tests/k6/results/summary.json": JSON.stringify(data, null, 2),
  };
}
