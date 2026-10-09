# RAG Ambiental - Ley Provincial 1875 de Neuquén

## 1. Descripción

Este proyecto implementa un sistema RAG (Retrieval-Augmented Generation)
orientado a la consulta preliminar de normativa ambiental de la provincia
del Neuquén.

El objetivo es facilitar el acceso a la normativa por parte de equipos como
Geología, Proyectos, Inmobiliario y GIS durante etapas tempranas de
planificación.

El sistema funciona como una herramienta de consulta y screening preliminar.
No reemplaza la evaluación ni el criterio profesional del equipo de Ambiente.


## 2. Problema

Durante la definición temprana de proyectos e infraestructura es necesario
considerar diferentes condicionantes ambientales.

La consulta e interpretación de estos requerimientos puede requerir la
intervención frecuente de especialistas ambientales, incluso para consultas
preliminares.

El proyecto busca facilitar el acceso a ese conocimiento utilizando lenguaje
natural, permitiendo identificar rápidamente información normativa relevante.


## 3. Justificación del uso de IA

Un buscador tradicional requiere que el usuario conozca previamente qué
términos, artículos o anexos debe consultar.

El uso de embeddings y modelos de lenguaje permite realizar consultas como:

"¿Qué aspectos ambientales debería considerar antes de definir una línea
de conducción?"

El sistema recupera semánticamente los fragmentos de normativa más relacionados
con la consulta y utiliza un modelo de lenguaje para elaborar una respuesta
basada en ese contexto.

Para esta PoC se utilizaron solo dos documentos como fuente de conocimiento,
sin embargo, la solución definitiva debería integrar más documentos reglamentarios.

## 4. Arquitectura

El sistema utiliza el siguiente flujo:

PDF
 ↓
Loader
 ↓
Cleaner
 ↓
Chunking
 ↓
Cohere Embeddings
 ↓
ChromaDB
 ↓
Retriever
 ↓
Cohere Rerank
 ↓
Cohere Chat
 ↓
Respuesta + fuentes

La aplicación se encuentra expuesta mediante FastAPI.

La aplicación se puede utilizar mediante streamlit.


## 5. Estructura del proyecto

rag-ambiental/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── rag/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── ingestion/
│   ├── loader.py
│   ├── cleaner.py
│   ├── chunker.py
│   └── ingest.py
│
├── data/
│   ├── raw/
│   └── chroma/
│
├── evaluation/
│   ├── dataset.json
│   ├── results.json
│   └── evaluate.py
|
├── frontend/
│   └── streamlit_app.py
|
├── tests/
│   ├── test_chunker.py
│   ├── test_cleaner.py
│   ├── test_loader.py
│   ├── test_retriever.py
│   ├── test_vector_store.py
│   └── test_embedidings.py
├── requirements.txt
├── .env
├── test_generator.py
├── test_pipeline_real.py
├── test_query.py
├── test_rerank_real.py
├── README.md
└── reset_collection.py

## 6. Componentes principales

### Loader

Extrae el texto de los documentos PDF y conserva metadata como documento
y página de origen.

### Cleaner

Normaliza espacios y saltos de línea del texto extraído, descarta las páginas
que quedan vacías y conserva la metadata de las páginas restantes.

### Chunker

Procesa cada página por separado y divide su texto en fragmentos de hasta
1.200 caracteres, con un solapamiento predeterminado de 200 caracteres entre
fragmentos consecutivos. Si encuentra un salto de línea después de la mitad
del fragmento, intenta usarlo como punto de corte. Luego elimina espacios al
inicio y al final de cada fragmento y omite los que queden vacíos.

Cada fragmento conserva la metadata original del documento y la página, y
agrega un índice de chunk. El identificador combina el nombre normalizado del
documento con un número secuencial. El solapamiento ayuda a mantener contexto
que podría quedar dividido entre dos fragmentos; el corte por página conserva
la referencia a la página de origen. El tamaño se mide en caracteres, no en
tokens.

### Embeddings

Cohere transforma los chunks y las preguntas de los usuarios en
representaciones vectoriales.

### Vector Store

ChromaDB almacena los embeddings, textos y metadata de los documentos.

### Retriever

Convierte la pregunta del usuario en un embedding y recupera desde ChromaDB
los chunks semánticamente más similares.

### Reranker

Cohere Rerank vuelve a ordenar los chunks recuperados según su relevancia
respecto de la consulta.

### Generator

El modelo generativo recibe la pregunta y los chunks seleccionados para
construir una respuesta fundamentada en el contexto recuperado.

### RAG Pipeline

Coordina el proceso:

Retriever -> Reranker -> Generator

Para cada consulta, el retriever obtiene hasta 10 candidatos desde ChromaDB.
Cohere Rerank los ordena por relevancia y conserva hasta 5 para el generador.
El generador responde usando la pregunta y esos fragmentos como contexto; la
respuesta incluye la referencia al documento y la página de cada fuente.


## 7. Ingesta

Los documentos deben colocarse en:

data/raw/

La ingesta puede ejecutarse con:

python -m ingestion.ingest

El proceso realiza:

PDF -> extracción -> chunking -> embeddings -> ChromaDB


## 8. Ejecución

Instalar las dependencias:

pip install -r requirements.txt

Configurar las variables de entorno en `.env`.

Ejemplo:

COHERE_API_KEY=...
EMBED_MODEL=...
RERANK_MODEL=...
CHAT_MODEL=...

CHROMA_PATH=./data/chroma
CHROMA_COLLECTION=normativa_ambiental

Levantar la API:

uvicorn app.main:app --reload

La documentación Swagger estará disponible en:

http://127.0.0.1:8000/docs
La interfaz Streamlit debe iniciarse en una segunda terminal, desde la raíz
del proyecto:

streamlit run frontend/streamlit_app.py

La interfaz estará disponible en:

http://localhost:8501

Mantén ambos procesos activos: Streamlit envía las consultas a FastAPI en
`http://127.0.0.1:8000/chat`.


## 9. API

### Health check

GET /health

### Consulta RAG

POST /chat

Ejemplo:

{
    "question": "¿Qué aspectos ambientales debo considerar para definir una instalación?"
}

La respuesta incluye:

- respuesta generada;
- documentos utilizados;
- páginas de origen.


## 10. Evaluación

Se creó un dataset de preguntas para evaluar el comportamiento del sistema.

La evaluación automatizada comprueba:

- si el sistema se abstiene cuando el dataset lo indica;
- si responde con al menos una fuente cuando se espera una respuesta;
- si la generación falla, por ejemplo, ante un error 422 de Cohere.

La clasificación de abstención se realiza con un modelo de Cohere y, si esa
llamada falla, se utiliza una heurística basada en expresiones de abstención.
Estos controles no verifican directamente la exactitud factual ni la
groundedness de cada afirmación, ni miden por sí solos la relevancia del
retrieval.

La evaluación puede ejecutarse con:

python -m evaluation.evaluation

En la corrida registrada en `evaluation/results.json`, aprobaron 8 de 10
preguntas (80 % de aprobación de estos controles; no representa una métrica de
exactitud factual). Los dos casos no aprobados fueron:

- **Q05:** Cohere devolvió un error 422 y no se generó una respuesta.
- **Q10:** el dataset esperaba una abstención, pero el evaluador clasificó la
  respuesta como sustantiva.

El archivo `evaluation/results.json` contiene las respuestas, las fuentes y el
resultado individual de cada pregunta.


## 11. IA Responsable y Human in the Loop

El sistema fue diseñado como herramienta de consulta preliminar y no como
un sistema autónomo de decisión ambiental.

El modelo tiene instrucciones explícitas para:

- responder utilizando el contexto recuperado;
- no inventar requisitos, restricciones o distancias;
- reconocer cuando la información disponible es insuficiente;
- no determinar automáticamente cumplimiento ambiental;
- no reemplazar la evaluación profesional del equipo de Ambiente.

Las decisiones sobre cumplimiento, aprobación o interpretación de situaciones
particulares permanecen bajo responsabilidad de especialistas humanos.

De esta manera, la IA facilita el acceso al conocimiento mientras que la
decisión final permanece bajo supervisión humana.


## 12. Limitaciones

La versión actual presenta las siguientes limitaciones:

- Solo utiliza la documentación incorporada a la base de conocimiento
- No realiza análisis espacial de una ubicación.
- No determina cumplimiento normativo.
- No reemplaza una evaluación de impacto ambiental.
- No reemplaza al especialista ambiental.
- La calidad de las respuestas depende de la calidad y actualización de los
  documentos incorporados.


## 13. Posibles mejoras

El proyecto puede evolucionar incorporando:

- normativa ambiental complementaria;
- chunking específico para documentos jurídicos y políticas empresariales;
- integración con información GIS;
- filtros mediante metadata;
- interfaz web;
- autenticación de usuarios;
- monitoreo de consultas;
- evaluación automatizada del RAG.


## 14. Tecnologías utilizadas

- Python
- FastAPI
- Cohere
- ChromaDB
- PyMuPDF
- Pydantic
- Pytest
- Streamlit

## 15. Conclusiones

Esta prueba de concepto muestra que un flujo RAG puede facilitar la consulta
preliminar de normativa ambiental mediante preguntas en lenguaje natural y
respuestas acompañadas por referencias al documento y la página recuperados.
La separación entre Streamlit y FastAPI permite mantener la interfaz y el
servicio de consulta como componentes independientes.

El alcance demostrado todavía es acotado: la base de conocimiento contiene
la Ley 1875 y el Decreto 2656, por lo que las respuestas no representan una
revisión exhaustiva de toda la normativa aplicable. En la evaluación
registrada, 8 de 10 preguntas aprobaron los controles implementados. Ese
resultado sirve como diagnóstico, pero no mide directamente la exactitud
factual ni garantiza que cada respuesta esté completamente respaldada por las
fuentes. Los fallos observados también muestran que deben mejorarse el manejo
de errores de generación y la abstención ante preguntas que exceden el
conocimiento disponible.

Antes de utilizar el sistema como apoyo operativo, conviene ampliar y
actualizar el corpus con fuentes oficiales pertinentes, evaluar la calidad
del retrieval y la fundamentación de las respuestas, y revisar los resultados
con especialistas de Ambiente. La herramienta agiliza el acceso a información,
pero no determina cumplimiento normativo ni reemplaza el criterio profesional
ni la aprobación humana. El uso de Cohere puede estar sujeto a cuotas y costos
según el modelo y el volumen de consultas.