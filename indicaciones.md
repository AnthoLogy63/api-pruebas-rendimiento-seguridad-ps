Tareas del Ejercicio 1 – Sistema de Biblioteca
1. Diseñar la entidad principal

Definir la información que almacenará un libro.

Ejemplo de atributos:

id
título
autor
ISBN
editorial
año de publicación
categoría
cantidad disponible
2. Diseñar los endpoints REST

Implementar como mínimo los siguientes servicios:

Método	Endpoint	Función
GET	/libros	Listar todos los libros
GET	/libros/<id>	Obtener un libro por ID
POST	/libros	Registrar un nuevo libro
PUT	/libros/<id>	Actualizar la información de un libro
DELETE	/libros/<id>	Eliminar un libro
3. Crear el proyecto en Flask

Organizar el proyecto (preferiblemente utilizando una arquitectura por capas):

routes
controllers
services
repositories
models
database
app.py
4. Implementar la base de datos

Utilizar SQLite como sistema de almacenamiento, ya que es ligero, no requiere instalar un servidor de base de datos y es suficiente para esta práctica.

Crear la tabla Libros con los atributos definidos.

5. Implementar el CRUD

Programar cada uno de los endpoints para realizar las operaciones sobre los libros.

6. Implementar validaciones

Validar que:

El título no esté vacío.
El autor no esté vacío.
El ISBN sea obligatorio.
El año sea un número válido.
La cantidad disponible sea un entero mayor o igual a 0.
No se pueda consultar, actualizar o eliminar un libro inexistente.

Responder con los códigos HTTP correspondientes:

200 OK
201 Created
400 Bad Request
404 Not Found
7. Preparar el proyecto para su ejecución

Generar el archivo requirements.txt con todas las dependencias necesarias para que cualquier integrante del equipo pueda instalar el entorno fácilmente mediante:

pip install -r requirements.txt

Además, incluir un breve apartado en el README.md indicando los pasos para ejecutar la API.

8. Probar la API

Verificar el funcionamiento de todos los endpoints utilizando Postman, Thunder Client o Insomnia.

Casos mínimos a probar:

Crear un libro.
Listar libros.
Buscar un libro por ID.
Actualizar un libro.
Eliminar un libro.
Probar casos de error (datos inválidos y recursos inexistentes).
9. Documentar la API

Preparar una breve documentación indicando:

Método HTTP.
Endpoint.
Descripción.
Ejemplo de solicitud (JSON).
Ejemplo de respuesta (JSON).
Códigos de respuesta.
Entregable final

Al finalizar se deberá contar con una API REST funcional para un Sistema de Biblioteca, desarrollada en Flask, con operaciones CRUD completas, validaciones básicas, almacenamiento en SQLite, un archivo requirements.txt para facilitar la instalación de dependencias y una breve documentación para que el resto del equipo pueda utilizar la API en las pruebas de rendimiento (JMeter y K6) y de seguridad.