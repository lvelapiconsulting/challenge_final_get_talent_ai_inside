import cohere

from app.core.config import settings


class EmbeddingService:

    def __init__(self):
        self.client = cohere.ClientV2(
            api_key=settings.cohere_api_key
        )

        self.model = settings.embed_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embed(
            model=self.model,
            texts=texts,
            input_type="search_document",
            embedding_types=["float"],
        )

        return response.embeddings.float

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embed(
            model=self.model,
            texts=[text],
            input_type="search_query",
            embedding_types=["float"],
        )

        return response.embeddings.float[0]