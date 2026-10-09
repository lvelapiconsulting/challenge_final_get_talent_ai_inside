from pathlib import Path

from ingestion.loader import load_pdf
from ingestion.cleaner import clean_pages
from ingestion.chunker import chunk_pages
from app.services.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore


def ingest_pdf(
    file_path: str,
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
) -> int:

    print(f"\nProcesando: {file_path}")

    # 1. Cargar PDF
    pages = load_pdf(file_path)
    print(f"  Paginas con texto: {len(pages)}")

    # 2. Limpiar texto
    pages = clean_pages(pages)

    # 3. Generar chunks
    chunks = chunk_pages(pages)
    print(f"  Chunks generados: {len(chunks)}")

    if not chunks:
        print("  ADVERTENCIA: no se generaron chunks.")
        return 0

    # 4. Preparar datos
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # 5. Generar embeddings
    embeddings = embedding_service.embed_documents(
        documents
    )

    # 6. Guardar en Chroma
    vector_store.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def ingest_directory(directory: str = "data/raw") -> None:

    directory_path = Path(directory)

    pdf_files = sorted(directory_path.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No se encontraron archivos PDF en {directory}"
        )

    print(f"PDF encontrados: {len(pdf_files)}")

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    total_chunks = 0

    for pdf_path in pdf_files:

        chunks = ingest_pdf(
            file_path=str(pdf_path),
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        total_chunks += chunks

    print("\n--- Ingesta completada ---")
    print(f"PDF procesados: {len(pdf_files)}")
    print(f"Chunks generados: {total_chunks}")
    print(f"Chunks en ChromaDB: {vector_store.count()}")


if __name__ == "__main__":
    ingest_directory()