import re


def clean_text(text: str) -> str:
    """
    Realiza una limpieza conservadora del texto extraído
    de documentos normativos.
    """

    # Reemplazar espacios no separables
    text = text.replace("\u00a0", " ")

    # Eliminar espacios y tabs repetidos
    text = re.sub(r"[ \t]+", " ", text)

    # Eliminar espacios antes de saltos de línea
    text = re.sub(r" +\n", "\n", text)

    # Evitar exceso de líneas vacías
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Eliminar espacios al principio y final
    return text.strip()


def clean_pages(pages: list[dict]) -> list[dict]:
    """
    Limpia el texto de las páginas manteniendo su metadata.
    """

    cleaned_pages = []

    for page in pages:

        text = clean_text(page["text"])

        if not text:
            continue

        cleaned_pages.append(
            {
                "text": text,
                "metadata": page["metadata"].copy(),
            }
        )

    return cleaned_pages