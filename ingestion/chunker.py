from pathlib import Path


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[dict]:
    """
    Divide las páginas en chunks conservando metadata.

    El ID de cada chunk incluye el nombre del documento
    para evitar colisiones entre distintos PDFs.
    """

    chunks = []
    chunk_id = 0

    for page in pages:
        text = page["text"]
        metadata = page["metadata"]

        # Obtener nombre del documento sin extensión
        document_name = metadata.get(
            "document",
            "document"
        )

        document_stem = Path(document_name).stem

        # Normalizar mínimamente para usarlo como ID
        document_id = (
            document_stem
            .lower()
            .replace(" ", "_")
        )

        start = 0

        while start < len(text):

            end = start + chunk_size
            chunk_text = text[start:end]

            # Intentar cortar por salto de línea
            if end < len(text):

                last_break = chunk_text.rfind("\n")

                if last_break > chunk_size * 0.5:
                    chunk_text = chunk_text[:last_break]
                    end = start + last_break

            chunk_text = chunk_text.strip()

            if chunk_text:

                chunk_name = (
                    f"{document_id}_chunk_{chunk_id:05d}"
                )

                chunks.append(
                    {
                        "id": chunk_name,
                        "text": chunk_text,
                        "metadata": {
                            **metadata,
                            "chunk": chunk_id,
                        },
                    }
                )

                chunk_id += 1

            # Mantener overlap entre chunks
            next_start = end - overlap

            if next_start <= start:
                next_start = end

            start = next_start

    return chunks