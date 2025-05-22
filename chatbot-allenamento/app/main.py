"""
Entry point FastAPI per il Chatbot Allenamento
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import get_rag_engine
from app.api.routes import chat, workout
from app.core.error_handler import setup_exception_handlers

# Configura logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestisce il ciclo di vita dell'applicazione"""
    logger.info("🚀 Avvio del Chatbot Allenamento...")
    
    # Inizializza il motore RAG in background
    try:
        logger.info("📚 Inizializzazione del motore RAG...")
        rag_engine = get_rag_engine()
        
        # Avvia l'inizializzazione in background
        asyncio.create_task(rag_engine.initialize())
        logger.info("✅ Motore RAG inizializzato con successo")
        
    except Exception as e:
        logger.error(f"❌ Errore nell'inizializzazione del motore RAG: {e}")
    
    yield
    
    logger.info("🔄 Arresto del Chatbot Allenamento...")

# Inizializza FastAPI
app = FastAPI(
    title="Chatbot Allenamento",
    description="Chatbot AI per la generazione di schede di allenamento personalizzate",
    version="1.0.0",
    lifespan=lifespan
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura gestione errori
setup_exception_handlers(app)

# Monta i file statici
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configura i template
templates = Jinja2Templates(directory="app/templates")

# Include le route API
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(workout.router, prefix="/api/v1", tags=["workout"])

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve la pagina principale del chatbot"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Endpoint per verificare lo stato dell'applicazione"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "rag_initialized": get_rag_engine().is_initialized()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
