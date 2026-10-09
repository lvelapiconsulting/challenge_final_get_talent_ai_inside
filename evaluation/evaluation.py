import json
from pathlib import Path

import cohere

from app.core.config import settings
from app.rag.pipeline import RAGPipeline

judge_client = cohere.ClientV2(api_key=settings.cohere_api_key)

JUDGE_PROMPT = """Clasifica la respuesta de un asistente a una pregunta.

Responde únicamente con una palabra:
- ABSTENCION: la respuesta, en lo esencial, indica que no tiene información
  suficiente para responder la pregunta, o se niega a determinarlo.
- RESPUESTA: la respuesta aporta contenido sustantivo que contesta la pregunta,
  aunque aclare al final que faltan algunos detalles.

Pregunta: {question}

Respuesta:
{answer}
"""


DATASET_PATH = Path("evaluation/dataset.json")
RESULTS_PATH = Path("evaluation/results.json")

ABSTENTION_MARKERS = [
    "no es suficiente",
    "no resulta suficiente",
    "no son suficientes",
    "información disponible no",
    "informacion disponible no",
    "no cuento con",
    "no se especifica",
    "no se menciona",
    "no se encuentra",
    "no contiene",
    "no proporciona",
    "no puedo determinar",
    "no puedo confirmar",
    "no determin",
    "no incluyen",
    "no hay información",
    "no hay informacion",
]


def is_abstention(answer: str | None) -> bool:
    """Heurística: detecta si la respuesta declina responder."""

    # Solo el inicio: una nota de "información insuficiente" al final no es abstención.
    text = (answer or "").lower()[:200]
    return any(marker in text for marker in ABSTENTION_MARKERS)


def judge_abstention(question: str, answer: str) -> bool:
    """Clasifica con un LLM si la respuesta es una abstención; usa la heurística si falla."""

    try:
        response = judge_client.chat(
            model=settings.chat_model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": JUDGE_PROMPT.format(question=question, answer=answer),
                }
            ],
        )
        verdict = response.message.content[0].text.strip().upper()
        return verdict.startswith("ABSTENCION")
    except Exception:
        return is_abstention(answer)


def check(item: dict, answer: str | None, sources: list[dict]) -> tuple[bool, str]:
    """Devuelve (aprobado, motivo)."""

    if answer is None:
        return False, "error de ejecución"

    if answer.startswith("No pude generar una respuesta"):
        return False, "falló la generación (Cohere 422)"

    abstained = judge_abstention(item["question"], answer)

    if item.get("should_abstain", False):
        if abstained:
            return True, "se abstuvo correctamente"
        return False, "debía abstenerse y respondió"

    if abstained:
        return False, "se abstuvo y debía responder"
    if not sources:
        return False, "respuesta sin fuentes"
    return True, "respondió con fuentes"


def load_dataset() -> list[dict]:
    """Carga las preguntas del dataset."""

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_results(results: list[dict]) -> None:
    """Guarda los resultados de la evaluación."""

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )


def evaluate() -> None:
    """Ejecuta las preguntas contra el pipeline RAG."""

    dataset = load_dataset()
    pipeline = RAGPipeline()

    results = []

    total = len(dataset)

    for index, item in enumerate(dataset, start=1):

        question_id = item["id"]
        question = item["question"]

        print(
            f"[{index}/{total}] "
            f"{question_id}: {question}"
        )

        try:
            result = pipeline.ask(question)

            evaluation_result = {
                "id": question_id,
                "question": question,
                "should_abstain": item.get(
                    "should_abstain",
                    False,
                ),
                "answer": result["answer"],
                "sources": result["sources"],
                "error": None,
            }

            passed, reason = check(item, result["answer"], result["sources"])
            evaluation_result["passed"] = passed
            evaluation_result["reason"] = reason

            print(f"{'PASS' if passed else 'FAIL'}: {reason}")

        except Exception as error:

            evaluation_result = {
                "id": question_id,
                "question": question,
                "should_abstain": item.get(
                    "should_abstain",
                    False,
                ),
                "answer": None,
                "sources": [],
                "error": str(error),
                "passed": False,
                "reason": "error de ejecución",
            }

            print(f"ERROR: {error}")

        results.append(evaluation_result)

    save_results(results)

    passed_count = sum(r["passed"] for r in results)

    print()
    print(f"Aprobadas: {passed_count}/{total}")
    print("Evaluación finalizada.")
    print(f"Resultados guardados en: {RESULTS_PATH}")


if __name__ == "__main__":
    evaluate()