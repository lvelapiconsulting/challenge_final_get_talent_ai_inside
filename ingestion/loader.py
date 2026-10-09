from pathlib import Path

import fitz


def load_pdf(file_path: str) -> list[dict]:
    """
    Extrae el texto de un PDF página por página.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
    document = fitz.open(path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        if not text:
            continue

        pages.append(
            {
                "text": text,
                "metadata": {
                    "document": path.name,
                    "page": page_number,
                },
            }
        )

    document.close()

    return pages