"""
Servidor de producción ligero para pruebas de rendimiento.
Ejecutar sin modo debug para resultados más realistas en JMeter/K6.

Uso:
    python run_server.py
"""
from waitress import serve

from app import app

if __name__ == "__main__":
    print("Biblioteca Nova — servidor en http://0.0.0.0:5000")
    print("Modo: producción (Waitress, sin debug)")
    serve(app, host="0.0.0.0", port=5000, threads=8)
