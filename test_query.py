from app.rag.retriever import Retriever


retriever = Retriever()

query = "¿Qué requisitos existen para la ubicación de instalaciones?"

results = retriever.retrieve(
    query=query,
    top_k=5
)

for i, (document, metadata, distance) in enumerate(
    zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ),
    start=1,
):
    print(f"\n--- Resultado {i} ---")
    print(f"Distancia: {distance}")
    print(f"Metadata: {metadata}")
    print(document)