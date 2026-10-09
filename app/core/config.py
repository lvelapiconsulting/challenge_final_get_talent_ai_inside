from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Cohere
    cohere_api_key: str
    embed_model: str
    rerank_model: str
    chat_model: str

    # ChromaDB
    chroma_path: str = "./data/chroma"
    chroma_collection: str = "normativa_ambiental"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()