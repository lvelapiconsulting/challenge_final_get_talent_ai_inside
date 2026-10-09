from app.rag.vector_store import VectorStore


def test_vector_store():

    # Collection exclusiva para testing
    store = VectorStore(
        collection_name="normativa_ambiental_test"
    )

    # Embedding ficticio
    embedding = [0.1, 0.2, 0.3]

    # Insertar documento
    store.add_documents(
        ids=["test_001"],
        documents=[
            "Las instalaciones deberán considerar aspectos ambientales."
        ],
        embeddings=[embedding],
        metadatas=[
            {
                "document": "test.pdf",
                "page": 1
            }
        ]
    )

    # Verificar que existe al menos un registro
    assert store.count() > 0

    # Buscar utilizando el mismo vector
    results = store.search(
        query_embedding=embedding,
        top_k=1
    )

    # Verificar resultado
    assert len(results["documents"][0]) > 0

    # Verificar contenido
    assert (
        results["documents"][0][0]
        == "Las instalaciones deberán considerar aspectos ambientales."
    )

    # Verificar metadata
    assert results["metadatas"][0][0]["document"] == "test.pdf"
    assert results["metadatas"][0][0]["page"] == 1

    # # Limpiar la colección de prueba
    # store.collection.delete()

    # # Verificar que la colección está vacía
    # assert store.count() == 0

    # Limpiar collection completa de testing
    store.client.delete_collection(
        name="normativa_ambiental_test"
    )