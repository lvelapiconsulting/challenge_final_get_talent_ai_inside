import cohere
from cohere.errors import UnprocessableEntityError

from app.core.config import settings
from app.rag.prompts import SYSTEM_PROMPT


class GeneratorService:

    def __init__(self):
        self.client = cohere.ClientV2(
            api_key=settings.cohere_api_key
        )

        self.model = settings.chat_model

    def generate(
        self,
        question: str,
        documents: list[dict],
    ) -> str:
        """
        Genera una respuesta utilizando la pregunta del usuario
        y los documentos recuperados por el RAG.
        """

        # Convertir nuestro formato interno al formato de Cohere
        cohere_documents = []

        for i, document in enumerate(documents, start=1):

            metadata = document.get("metadata", {})

            cohere_documents.append(
                {
                    "id": f"doc_{i}",
                    "data": {
                        "text": document["text"],
                        "document": metadata.get("document", ""),
                        "page": str(metadata.get("page", "")),
                    },
                }
            )

        # Generar respuesta
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                documents=cohere_documents,
            )
        except UnprocessableEntityError:
            # Cohere devuelve 422 cuando no puede generar respuesta (p. ej. pregunta sin sentido)
            return (
                "No pude generar una respuesta para esa consulta. "
                "Reformula la pregunta con más detalle."
            )

        for content_item in response.message.content:
            if content_item.type == "text":
                return content_item.text

        raise ValueError("Cohere no devolvió contenido de tipo texto.")