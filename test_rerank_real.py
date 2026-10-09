from app.rag.retriever import Retriever
from app.services.reranker import RerankerService


query = "¿Qué requisitos existen para la ubicación de instalaciones?"

retriever = Retriever()
reranker = RerankerService()


# 1. Recuperar 10 candidatos reales desde Chroma
results = retriever.retrieve(
    query=query,
    top_k=10
)


# 2. Convertir la respuesta de Chroma al formato
# que espera nuestro RerankerService
documents = []

for document, metadata, distance in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0],
):
    documents.append(
        {
            "text": document,
            "metadata": metadata,
            "distance": distance,
        }
    )


# 3. Mostrar ranking original de Chroma
print("\n=== RESULTADOS CHROMA ===\n")

for i, doc in enumerate(documents, start=1):

    print(f"--- Resultado {i} ---")
    print(f"Distancia Chroma: {doc['distance']:.4f}")
    print(f"Metadata: {doc['metadata']}")
    print(doc["text"][:300])
    print()


# 4. Aplicar Cohere Rerank
reranked = reranker.rerank(
    query=query,
    documents=documents,
    top_n=2,
)


# 5. Mostrar nuevo ranking
print("\n=== RESULTADOS RERANK ===\n")

for i, doc in enumerate(reranked, start=1):

    print(f"--- Resultado {i} ---")
    print(f"Relevance: {doc['relevance_score']:.4f}")
    print(f"Distancia Chroma original: {doc['distance']:.4f}")
    print(f"Metadata: {doc['metadata']}")
    print(doc["text"][:300])
    print()