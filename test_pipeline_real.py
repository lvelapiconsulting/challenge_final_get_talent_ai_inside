from app.rag.pipeline import RAGPipeline


pipeline = RAGPipeline()

result = pipeline.ask(
    "¿Es necesatrio un estudio de impacto ambiental para instalaciones de oleoductos?"
)

print("\n=== RESPUESTA ===")
print(result["answer"])

print("\n=== FUENTES ===")
for source in result["sources"]:
    print(source)