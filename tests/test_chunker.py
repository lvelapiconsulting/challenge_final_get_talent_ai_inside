from ingestion.chunker import chunk_pages


def test_chunk_pages_creates_chunks():

    pages = [
        {
            "text": "A" * 3000,
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 1,
            },
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=100,
    )

    # Un texto grande debe producir varios chunks
    assert len(chunks) > 1


def test_chunk_preserves_metadata():

    pages = [
        {
            "text": "Contenido ambiental de prueba.",
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 15,
            },
        }
    ]

    chunks = chunk_pages(pages)

    assert len(chunks) == 1

    assert chunks[0]["metadata"]["document"] == "ley_1875.pdf"
    assert chunks[0]["metadata"]["page"] == 15
    assert "chunk" in chunks[0]["metadata"]


def test_chunk_has_unique_ids():

    pages = [
        {
            "text": "B" * 3000,
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 1,
            },
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=100,
    )

    ids = [chunk["id"] for chunk in chunks]

    # No debe haber IDs duplicados
    assert len(ids) == len(set(ids))


def test_short_text_creates_single_chunk():

    pages = [
        {
            "text": "Artículo 1. Texto corto de prueba.",
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 1,
            },
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=100,
    )

    assert len(chunks) == 1

    assert chunks[0]["text"] == (
        "Artículo 1. Texto corto de prueba."
    )