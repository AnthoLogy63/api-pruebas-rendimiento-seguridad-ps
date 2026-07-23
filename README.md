# Biblioteca Nova

**Biblioteca Nova** — *Donde cada página abre un universo*

API REST y panel web para gestión de catálogo y préstamos de biblioteca. Desarrollada en Flask con SQLite, arquitectura por capas y lista para pruebas de rendimiento (JMeter, K6) y seguridad.

## Características

- CRUD completo de libros con validaciones
- Módulo de préstamos con control de inventario
- Panel web elegante conectado a la API
- Seed de datos de prueba
- Scripts K6 y plan JMeter incluidos

## Estructura del proyecto

```
API-PROBBED/
├── app.py                      # Punto de entrada (modo desarrollo)
├── run_server.py               # Servidor para pruebas de rendimiento
├── seed.py                     # Datos de prueba
├── requirements.txt
├── templates/index.html        # Panel web Biblioteca Nova
├── static/css/style.css
├── static/js/app.js
├── database/db.py
├── models/                     # Entidades Libro, Prestamo
├── repositories/               # Acceso a datos
├── services/                   # Lógica de negocio
├── controllers/                # Controladores HTTP
├── routes/                     # Blueprints REST + web
└── tests/
    ├── k6/load_test.js         # Prueba de carga K6
    └── jmeter/                 # Plan JMeter + CSV
```

## Requisitos

- Python 3.10+
- pip
- (Opcional) K6 y Apache JMeter para pruebas de rendimiento

## Instalación rápida

```powershell
# 1. Clonar el repositorio
cd API-PROBBED

# 2. Entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Dependencias
pip install -r requirements.txt

# 4. Cargar datos de prueba
python seed.py --reset

# 5. Iniciar la aplicación
python app.py
```

Abrir en el navegador: **http://localhost:5000**

## Endpoints API

### Libros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/biblioteca/estado` | Estado del sistema de biblioteca |
| GET | `/health` | Alias técnico (JMeter/K6) |
| GET | `/libros` | Listar libros |
| GET | `/libros/<id>` | Obtener libro |
| POST | `/libros` | Crear libro |
| PUT | `/libros/<id>` | Actualizar libro |
| DELETE | `/libros/<id>` | Eliminar libro |
| GET | `/libros/buscar?titulo=&autor=&categoria=` | Buscar |
| GET | `/libros/categorias` | Categorías |
| GET | `/libros/estadisticas` | Estadísticas |

### Préstamos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/prestamos` | Listar todos |
| GET | `/prestamos/activos` | Préstamos activos |
| GET | `/prestamos/<id>` | Obtener préstamo |
| POST | `/prestamos` | Registrar préstamo |
| PUT | `/prestamos/<id>/devolver` | Devolver libro |
| GET | `/prestamos/estadisticas` | Estadísticas |

Documentación completa: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Seed de datos

```bash
python seed.py          # Inserta si la BD está vacía
python seed.py --reset  # Borra y recarga 15 libros + 6 préstamos
```

## Pruebas de rendimiento

### Modo recomendado (sin debug)

```bash
python run_server.py
```

### K6

```bash
k6 run tests/k6/load_test.js
```

### Apache JMeter

1. Abrir `tests/jmeter/biblioteca_nova.jmx`
2. Ejecutar el Thread Group (25 usuarios, 5 loops)

Guía detallada: [tests/README.md](tests/README.md)

## Pruebas funcionales

```bash
python test_api.py
```

## Panel web

El panel en `/` permite:

- Ver dashboard con estadísticas en tiempo real
- Gestionar catálogo de libros (crear, editar, eliminar)
- Registrar y devolver préstamos
- Buscar libros en el catálogo

## Códigos HTTP

| Código | Uso |
|--------|-----|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 400 | Datos inválidos |
| 404 | Recurso no encontrado |
| 409 | Conflicto (ISBN duplicado, sin stock, préstamo activo) |

## Equipo — checklist para pruebas

- [ ] `pip install -r requirements.txt`
- [ ] `python seed.py --reset`
- [ ] `python app.py` o `python run_server.py`
- [ ] Verificar `http://localhost:5000/biblioteca/estado`
- [ ] Ejecutar K6 o JMeter según corresponda
