from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.services.embeddings import EmbeddingService


def test_retriever():

    collection_name = "retriever_test"

    # Crear servicios
    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        collection_name=collection_name
    )

    # Documentos de prueba
    documents = [
        "Las líneas de conducción deben ser inspeccionadas periódicamente.",
        "Los residuos deben gestionarse de acuerdo con la normativa ambiental.",
        "La ubicación de instalaciones debe considerar los recursos hídricos.",
    ]

    ids = [
        "test_lineas",
        "test_residuos",
        "test_agua",
    ]

    metadatas = [
        {"document": "test.pdf", "page": 1},
        {"document": "test.pdf", "page": 2},
        {"document": "test.pdf", "page": 3},
    ]

    # Generar embeddings reales con Cohere
    embeddings = embedding_service.embed_documents(documents)

    # Guardar documentos en Chroma
    vector_store.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    # Crear Retriever
    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # Consulta semántica
    results = retriever.retrieve(
        query="¿Qué debería considerar respecto al agua al ubicar una instalación?",
        top_k=1,
    )

    # Comprobar que devuelve resultados
    assert len(results["documents"][0]) == 1

    retrieved_document = results["documents"][0][0]

    # Esperamos recuperar el documento relacionado con recursos hídricos
    assert "recursos hídricos" in retrieved_document

    # Limpiar collection de prueba
    vector_store.client.delete_collection(
        name=collection_name
    )