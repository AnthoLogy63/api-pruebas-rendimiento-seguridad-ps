# Documentación de la API - Biblioteca Nova

Base URL: `http://localhost:5000`

Panel web: `http://localhost:5000/`

Todas las respuestas exitosas incluyen `"success": true`. Los errores incluyen `"success": false` y un campo `"error"` con el mensaje.

---

## 1. Estado de la biblioteca

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/biblioteca/estado` |
| **Descripción** | Verifica que el sistema de biblioteca esté en línea |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "estado": "operativa",
  "biblioteca": "Biblioteca Nova",
  "mensaje": "Sistema de biblioteca en línea",
  "version": "2.0.0"
}
```

> **Nota:** `/health` existe como alias técnico para herramientas de monitoreo y pruebas de rendimiento (JMeter, K6). La app web usa `/biblioteca/estado`.

---

## 2. Listar todos los libros

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/libros` |
| **Descripción** | Obtiene la lista completa de libros registrados |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "total": 2,
  "data": [
    {
      "id": 1,
      "titulo": "Cien años de soledad",
      "autor": "Gabriel García Márquez",
      "isbn": "978-0307474728",
      "editorial": "Sudamericana",
      "anio_publicacion": 1967,
      "categoria": "Novela",
      "cantidad_disponible": 5,
      "created_at": "2026-07-23 18:00:00",
      "updated_at": "2026-07-23 18:00:00"
    }
  ]
}
```

---

## 3. Obtener libro por ID

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/libros/<id>` |
| **Descripción** | Obtiene la información de un libro específico |

**Ejemplo de solicitud:**
```
GET /libros/1
```

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "titulo": "Cien años de soledad",
    "autor": "Gabriel García Márquez",
    "isbn": "978-0307474728",
    "editorial": "Sudamericana",
    "anio_publicacion": 1967,
    "categoria": "Novela",
    "cantidad_disponible": 5,
    "created_at": "2026-07-23 18:00:00",
    "updated_at": "2026-07-23 18:00:00"
  }
}
```

**Respuesta de error (404 Not Found):**
```json
{
  "success": false,
  "error": "Libro con id 999 no encontrado"
}
```

---

## 4. Crear un libro

| Campo | Valor |
|-------|-------|
| **Método** | POST |
| **Endpoint** | `/libros` |
| **Descripción** | Registra un nuevo libro en el catálogo |
| **Content-Type** | `application/json` |

**Ejemplo de solicitud:**
```json
{
  "titulo": "El Quijote de la Mancha",
  "autor": "Miguel de Cervantes",
  "isbn": "978-8420412146",
  "editorial": "Alfaguara",
  "anio_publicacion": 1605,
  "categoria": "Clásico",
  "cantidad_disponible": 3
}
```

**Campos obligatorios:** `titulo`, `autor`, `isbn`, `anio_publicacion`, `cantidad_disponible`

**Ejemplo de respuesta (201 Created):**
```json
{
  "success": true,
  "message": "Libro creado",
  "data": {
    "id": 2,
    "titulo": "El Quijote de la Mancha",
    "autor": "Miguel de Cervantes",
    "isbn": "978-8420412146",
    "editorial": "Alfaguara",
    "anio_publicacion": 1605,
    "categoria": "Clásico",
    "cantidad_disponible": 3,
    "created_at": "2026-07-23 18:05:00",
    "updated_at": "2026-07-23 18:05:00"
  }
}
```

**Respuesta de error (400 Bad Request):**
```json
{
  "success": false,
  "error": "El campo 'titulo' no puede estar vacío"
}
```

**Respuesta de error (409 Conflict - ISBN duplicado):**
```json
{
  "success": false,
  "error": "Ya existe un libro con ISBN 978-8420412146"
}
```

---

## 5. Actualizar un libro

| Campo | Valor |
|-------|-------|
| **Método** | PUT |
| **Endpoint** | `/libros/<id>` |
| **Descripción** | Actualiza la información de un libro existente |
| **Content-Type** | `application/json` |

**Ejemplo de solicitud:**
```json
{
  "titulo": "El Quijote de la Mancha",
  "autor": "Miguel de Cervantes",
  "isbn": "978-8420412146",
  "editorial": "Alfaguara",
  "anio_publicacion": 1605,
  "categoria": "Clásico",
  "cantidad_disponible": 8
}
```

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Libro actualizado",
  "data": {
    "id": 2,
    "titulo": "El Quijote de la Mancha",
    "autor": "Miguel de Cervantes",
    "isbn": "978-8420412146",
    "editorial": "Alfaguara",
    "anio_publicacion": 1605,
    "categoria": "Clásico",
    "cantidad_disponible": 8,
    "created_at": "2026-07-23 18:05:00",
    "updated_at": "2026-07-23 18:10:00"
  }
}
```

**Respuesta de error (404 Not Found):**
```json
{
  "success": false,
  "error": "Libro con id 999 no encontrado"
}
```

---

## 6. Eliminar un libro

| Campo | Valor |
|-------|-------|
| **Método** | DELETE |
| **Endpoint** | `/libros/<id>` |
| **Descripción** | Elimina un libro del catálogo |

**Ejemplo de solicitud:**
```
DELETE /libros/2
```

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Libro eliminado"
}
```

**Respuesta de error (404 Not Found):**
```json
{
  "success": false,
  "error": "Libro con id 999 no encontrado"
}
```

---

## 7. Buscar libros (endpoint adicional)

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/libros/buscar` |
| **Descripción** | Busca libros por título, autor y/o categoría (filtros opcionales) |

**Parámetros de consulta (query params):**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `titulo` | string | Búsqueda parcial por título |
| `autor` | string | Búsqueda parcial por autor |
| `categoria` | string | Búsqueda parcial por categoría |

**Ejemplo de solicitud:**
```
GET /libros/buscar?autor=García&categoria=Novela
```

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "total": 1,
  "data": [
    {
      "id": 1,
      "titulo": "Cien años de soledad",
      "autor": "Gabriel García Márquez",
      "isbn": "978-0307474728",
      "editorial": "Sudamericana",
      "anio_publicacion": 1967,
      "categoria": "Novela",
      "cantidad_disponible": 5,
      "created_at": "2026-07-23 18:00:00",
      "updated_at": "2026-07-23 18:00:00"
    }
  ]
}
```

---

## 8. Listar categorías (endpoint adicional)

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/libros/categorias` |
| **Descripción** | Devuelve las categorías distintas registradas en el catálogo |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "total": 3,
  "data": ["Clásico", "Novela", "Ciencia Ficción"]
}
```

---

## 9. Estadísticas del catálogo (endpoint adicional)

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/libros/estadisticas` |
| **Descripción** | Devuelve métricas agregadas del catálogo (útil para pruebas de rendimiento) |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_libros": 10,
    "total_ejemplares_disponibles": 45,
    "libros_por_categoria": [
      {"categoria": "Novela", "cantidad": 5},
      {"categoria": "Clásico", "cantidad": 3},
      {"categoria": "Sin categoría", "cantidad": 2}
    ]
  }
}
```

---

## 10. Listar préstamos

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/prestamos` |
| **Descripción** | Lista todos los préstamos registrados |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "total": 1,
  "data": [
    {
      "id": 1,
      "libro_id": 1,
      "nombre_usuario": "Ana Martínez",
      "email": "ana.martinez@email.com",
      "fecha_prestamo": "2026-07-20 10:00:00",
      "fecha_devolucion_esperada": "2026-08-03 10:00:00",
      "fecha_devolucion_real": null,
      "estado": "activo",
      "libro_titulo": "Cien años de soledad",
      "libro_autor": "Gabriel García Márquez"
    }
  ]
}
```

---

## 11. Listar préstamos activos

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/prestamos/activos` |
| **Descripción** | Lista solo préstamos con estado activo |

---

## 12. Obtener préstamo por ID

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/prestamos/<id>` |
| **Descripción** | Obtiene un préstamo específico |

---

## 13. Registrar préstamo

| Campo | Valor |
|-------|-------|
| **Método** | POST |
| **Endpoint** | `/prestamos` |
| **Descripción** | Registra un préstamo y descuenta 1 ejemplar del inventario |
| **Content-Type** | `application/json` |

**Ejemplo de solicitud:**
```json
{
  "libro_id": 1,
  "nombre_usuario": "Ana Martínez",
  "email": "ana.martinez@email.com",
  "dias_prestamo": 14
}
```

**Campos obligatorios:** `libro_id`, `nombre_usuario`, `email`

**Ejemplo de respuesta (201 Created):**
```json
{
  "success": true,
  "message": "Préstamo registrado",
  "data": {
    "id": 1,
    "libro_id": 1,
    "nombre_usuario": "Ana Martínez",
    "email": "ana.martinez@email.com",
    "fecha_prestamo": "2026-07-23 18:00:00",
    "fecha_devolucion_esperada": "2026-08-06 18:00:00",
    "fecha_devolucion_real": null,
    "estado": "activo",
    "libro_titulo": "Cien años de soledad",
    "libro_autor": "Gabriel García Márquez"
  }
}
```

**Errores:**
- 404 — Libro no encontrado
- 409 — Sin ejemplares disponibles

---

## 14. Devolver préstamo

| Campo | Valor |
|-------|-------|
| **Método** | PUT |
| **Endpoint** | `/prestamos/<id>/devolver` |
| **Descripción** | Marca el préstamo como devuelto y restaura el inventario |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "message": "Libro devuelto",
  "data": {
    "id": 1,
    "estado": "devuelto",
    "fecha_devolucion_real": "2026-07-23 19:00:00"
  }
}
```

---

## 15. Estadísticas de préstamos

| Campo | Valor |
|-------|-------|
| **Método** | GET |
| **Endpoint** | `/prestamos/estadisticas` |
| **Descripción** | Métricas agregadas de préstamos |

**Ejemplo de respuesta (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_prestamos": 6,
    "prestamos_activos": 5,
    "prestamos_devueltos": 1,
    "prestamos_vencidos": 1
  }
}
```

---

## Códigos de respuesta HTTP

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| 200 | OK | Operaciones exitosas (GET, PUT, DELETE) |
| 201 | Created | Libro creado exitosamente |
| 400 | Bad Request | Datos inválidos o campos obligatorios faltantes |
| 404 | Not Found | Libro o ruta no encontrada |
| 405 | Method Not Allowed | Método HTTP no soportado en la ruta |
| 409 | Conflict | ISBN duplicado, sin stock, préstamo ya devuelto, libro con préstamos activos |
| 500 | Internal Server Error | Error inesperado del servidor |

---

## Casos de prueba recomendados

### Casos exitosos
1. `POST /libros` — Crear un libro con datos válidos → 201
2. `GET /libros` — Listar todos los libros → 200
3. `GET /libros/1` — Obtener libro existente → 200
4. `PUT /libros/1` — Actualizar libro existente → 200
5. `DELETE /libros/1` — Eliminar libro existente → 200

### Casos de error
1. `POST /libros` con título vacío → 400
2. `POST /libros` con cantidad negativa → 400
3. `POST /libros` con año inválido → 400
4. `GET /libros/999` — ID inexistente → 404
5. `PUT /libros/999` — Actualizar inexistente → 404
6. `DELETE /libros/999` — Eliminar inexistente → 404
7. `POST /libros` con ISBN duplicado → 409
