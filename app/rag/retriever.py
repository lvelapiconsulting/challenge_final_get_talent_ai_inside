from app.services.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> dict:

        # 1. Generar embedding de la consulta
        query_embedding = self.embedding_service.embed_query(query)

        # 2. Buscar documentos similares
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return results