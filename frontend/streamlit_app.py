import requests
import streamlit as st


# URL de nuestra API FastAPI
API_URL = "http://127.0.0.1:8000/chat"


# -------------------------------------------------
# Configuración de la página
# -------------------------------------------------

st.set_page_config(
    page_title="Asistente Ambiental",
    page_icon="🌱",
    layout="centered",
)


# -------------------------------------------------
# Encabezado
# -------------------------------------------------

st.title("🌱 Asistente Ambiental")

st.caption(
    "Consulta preliminar de normativa ambiental "
    "de la Provincia del Neuquén"
)

st.info(
    "Este asistente brinda orientación preliminar basada en "
    "la normativa disponible. Las respuestas no reemplazan "
    "la evaluación del equipo de Ambiente."
)


# -------------------------------------------------
# Historial de mensajes
# -------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# Mostrar mensajes existentes
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Mostrar fuentes de las respuestas del asistente
        if message.get("sources"):

            with st.expander("📚 Fuentes consultadas"):

                for source in message["sources"]:

                    document = source.get(
                        "document",
                        "Documento"
                    )

                    page = source.get("page")

                    if page is not None:
                        st.write(
                            f"📄 {document} - Página {page}"
                        )
                    else:
                        st.write(
                            f"📄 {document}"
                        )


# -------------------------------------------------
# Input del usuario
# -------------------------------------------------

question = st.chat_input(
    "Escribí tu consulta ambiental..."
)


if question:

    # ---------------------------------------------
    # Guardar pregunta
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Mostrar pregunta
    with st.chat_message("user"):
        st.markdown(question)


    # ---------------------------------------------
    # Consultar la API
    # ---------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Consultando normativa..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "question": question
                    },
                    timeout=90,
                )

                response.raise_for_status()

                data = response.json()

                answer = data["answer"]
                sources = data.get("sources", [])


                # ---------------------------------
                # Mostrar respuesta
                # ---------------------------------

                st.markdown(answer)


                # ---------------------------------
                # Mostrar fuentes
                # ---------------------------------

                if sources:

                    with st.expander(
                        "📚 Fuentes consultadas"
                    ):

                        for source in sources:

                            document = source.get(
                                "document",
                                "Documento"
                            )

                            page = source.get("page")

                            if page is not None:
                                st.write(
                                    f"📄 {document} - Página {page}"
                                )
                            else:
                               st.write(
                                    f"📄 {document}"
                                )


                # ---------------------------------
                # Guardar respuesta en historial
                # ---------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )


            except requests.exceptions.ConnectionError:

                st.error(
                    "No se pudo conectar con FastAPI. "
                    "Verificá que la API esté ejecutándose."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "La consulta tardó demasiado tiempo."
                )


            except requests.exceptions.HTTPError:

                try:
                    error_detail = response.json().get(
                        "detail",
                        "Error desconocido"
                    )
                except Exception:
                    error_detail = response.text

                st.error(
                    f"Error de la API: {error_detail}"
                )


            except Exception as error:

                st.error(
                    f"Ocurrió un error inesperado: {error}"
                )