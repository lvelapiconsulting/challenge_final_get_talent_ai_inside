from app.rag.retriever import Retriever
from app.services.reranker import RerankerService
from app.services.generator import GeneratorService

class RAGPipeline:

    def __init__(
        self,
        retriever: Retriever | None = None,
        reranker: RerankerService | None = None,
        generator: GeneratorService | None = None,
    ):
        self.retriever = retriever or Retriever()
        self.reranker = reranker or RerankerService()
        self.generator = generator or GeneratorService()

    def ask(
        self,
        question: str,
        retrieval_k: int = 10,
        rerank_k: int = 5,
    ) -> dict:

        # 1. Recuperar candidatos desde Chroma
        results = self.retriever.retrieve(
            query=question,
            top_k=retrieval_k,
        )

        # 2. Convertir la respuesta de Chroma
        # a nuestro formato interno
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

        # 3. Rerankear los documentos recuperados
        reranked_documents = self.reranker.rerank(
            query=question,
            documents=documents,
            top_n=rerank_k,
        )

        # 4. Generar respuesta
        answer = self.generator.generate(
            question=question,
            documents=reranked_documents,
        )

        # 5. Preparar fuentes
        sources = []

        for document in reranked_documents:
            metadata = document.get("metadata", {})

            sources.append(
                {
                    "document": metadata.get("document", ""),
                    "page": metadata.get("page"),
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }