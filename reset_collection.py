from app.rag.vector_store import VectorStore
from app.core.config import settings


store = VectorStore()

collection_name = settings.chroma_collection

print(f"Collection actual: {collection_name}")
print(f"Chunks actuales: {store.count()}")

# Eliminar collection
store.client.delete_collection(
    name=collection_name
)

print("Collection eliminada.")

# Crear nuevamente la collection vacía
store.collection = store.client.get_or_create_collection(
    name=collection_name
)

print(f"Collection recreada.")
print(f"Chunks actuales: {store.count()}")