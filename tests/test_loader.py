from ingestion.loader import load_pdf


def test_load_pdf():

    pages = load_pdf("data/raw/ley_1875.pdf")

    assert len(pages) > 0
    assert "text" in pages[0]
    assert "metadata" in pages[0]
    assert "page" in pages[0]["metadata"]

    print(pages[0])