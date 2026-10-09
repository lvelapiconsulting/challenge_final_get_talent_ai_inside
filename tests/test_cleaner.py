from ingestion.cleaner import clean_text, clean_pages


def test_clean_text_removes_extra_spaces():

    text = "Ley     Provincial     1875"

    result = clean_text(text)

    assert result == "Ley Provincial 1875"


def test_clean_text_preserves_structure():

    text = """
ARTÍCULO 1°
La presente Ley establece...

ARTÍCULO 2°
La autoridad de aplicación...
"""

    result = clean_text(text)

    assert "ARTÍCULO 1°" in result
    assert "ARTÍCULO 2°" in result
    assert "La presente Ley establece..." in result


def test_clean_pages_preserves_metadata():

    pages = [
        {
            "text": "  ARTÍCULO 1°    Texto de prueba.  ",
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 10,
            },
        }
    ]

    result = clean_pages(pages)

    assert len(result) == 1

    assert result[0]["text"] == "ARTÍCULO 1° Texto de prueba."

    assert result[0]["metadata"]["document"] == "ley_1875.pdf"
    assert result[0]["metadata"]["page"] == 10


def test_clean_pages_removes_empty_pages():

    pages = [
        {
            "text": "     ",
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 1,
            },
        },
        {
            "text": "ARTÍCULO 1° Texto válido.",
            "metadata": {
                "document": "ley_1875.pdf",
                "page": 2,
            },
        },
    ]

    result = clean_pages(pages)

    assert len(result) == 1
    assert result[0]["metadata"]["page"] == 2