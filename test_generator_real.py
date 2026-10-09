from app.rag.retriever import Retriever
from app.services.reranker import RerankerService
from app.services.generator import GeneratorService


query = "¿Qué requisitos existen para la ubicación de instalaciones?"

# Inicializar componentes
retriever = Retriever()
reranker = RerankerService()
generator = GeneratorService()


# 1. Recuperar candidatos desde Chroma
results = retriever.retrieve(
    query=query,
    top_k=10,
)


# 2. Convertir resultado de Chroma al formato interno
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


# 3. Rerankear y conservar los 5 mejores
reranked_documents = reranker.rerank(
    query=query,
    documents=documents,
    top_n=5,
)


# 4. Mostrar contexto que recibirá el Generator
print("\n=== CONTEXTO RERANKEADO ===\n")

for i, doc in enumerate(reranked_documents, start=1):
    print(f"--- Chunk {i} ---")
    print(f"Relevance: {doc['relevance_score']:.4f}")
    print(f"Metadata: {doc['metadata']}")
    print(doc["text"][:500])
    print()


# 5. Preparar documentos para Cohere Chat
generator_documents = []

for i, doc in enumerate(reranked_documents, start=1):
    generator_documents.append(
        {
            "id": f"doc_{i}",
            "text": doc["text"],
        }
    )


# 6. Generar respuesta final
answer = generator.generate(
    question=query,
    documents=generator_documents,
)


# 7. Mostrar respuesta
print("\n=== RESPUESTA GENERADA ===\n")
print(answer)