import cohere

from app.core.config import settings


class RerankerService:

    def __init__(self):
        self.client = cohere.ClientV2(
            api_key=settings.cohere_api_key
        )

        self.model = settings.rerank_model

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_n: int = 5
    ) -> list[dict]:  # Cohere necesita los textos a evaluar
        texts = [doc["text"] for doc in documents]

        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=texts,
            top_n=top_n
        )

        # Reconstruimos los documentos originales
        # conservando metadata, id, pagina, etc.
        reranked_documents = []

        for result in response.results:
            document = documents[result.index].copy()

            document["relevance_score"] = result.relevance_score

            reranked_documents.append(document)

        return reranked_documents