from fastapi import FastAPI  # Importa FastAPI para crear la aplicación web.
from app.api.routes import router  # Importa las rutas definidas en el módulo de la API.

app = FastAPI(  # Crea la instancia principal de la aplicación.
    title="RAG Ambiental Neuquén",  # Define el título que aparecerá en la documentación de la API.
    description="Asistente para consulta preliminar de normativa ambiental.",
    version="0.1.0",  # Indica la versión actual de la API.
)  # Termina la configuración de la aplicación.

app.include_router(router)  # Registra en la aplicación las rutas importadas.

@app.get("/health")  # Crea el endpoint GET /health para comprobar que la API responde.
def health():  # Define la función que se ejecuta al llamar a ese endpoint.
    return {"status": "ok"}  # Devuelve una respuesta JSON indicando que el servicio está activo.