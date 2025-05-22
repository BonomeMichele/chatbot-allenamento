"""
Configurazioni dell'applicazione
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

class Settings:
    """Configurazioni dell'applicazione"""
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DOCUMENTS_PATH: Path = BASE_DIR / "app" / "static" / "documents"
    DATA_PATH: Path = BASE_DIR / "app" / "data"
    VECTOR_STORE_PATH: Path = BASE_DIR / "app" / "data" / "indexes"
    CHATS_PATH: Path = BASE_DIR / "app" / "data" / "chats"
    WORKOUTS_PATH: Path = BASE_DIR / "app" / "data" / "workouts"
    
    # Supporti file type
    SUPPORTED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt"]
    
    # RAG Settings
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 200
    TOP_K_DOCUMENTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    def __post_init__(self):
        """Crea le directory necessarie"""
        self.DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        self.CHATS_PATH.mkdir(parents=True, exist_ok=True)
        self.WORKOUTS_PATH.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Valida le configurazioni essenziali"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY non configurata nel file .env")
        return True

# Istanza globale delle configurazioni
settings = Settings()
settings.__post_init__()
settings.validate()
