import chromadb

from app.core.config import settings


class VectorStore:

    def __init__(self, collection_name: str | None = None):

        # Cliente local persistente de ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_path
        )

        # Si no se proporciona una collection,
        # utilizamos la configurada en .env
        name = collection_name or settings.chroma_collection

        # Obtiene la collection si existe o la crea si no existe
        self.collection = self.client.get_or_create_collection(
            name=name
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """
        Agrega documentos y sus embeddings a ChromaDB.
        """

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> dict:
        """
        Busca los documentos más similares al embedding
        proporcionado.
        """

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )
        return results

    def count(self) -> int:
        """
        Devuelve la cantidad de documentos almacenados
        en la colección.
        """
        return self.collection.count()