from app.services.embeddings import EmbeddingService


def test_embed_query():

    service = EmbeddingService()

    embedding = service.embed_query(
        "protección de recursos hídricos"
    )

    assert embedding is not None
    assert len(embedding) > 0

    print(f"Dimensión: {len(embedding)}")