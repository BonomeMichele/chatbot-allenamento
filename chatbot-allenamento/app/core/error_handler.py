"""
Gestione errori centralizzata
"""

import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class ChatbotException(Exception):
    """Eccezione base per il chatbot"""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class RAGException(ChatbotException):
    """Eccezione per errori del motore RAG"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "RAG_ERROR", details)

class LLMException(ChatbotException):
    """Eccezione per errori del LLM"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "LLM_ERROR", details)

class ValidationException(ChatbotException):
    """Eccezione per errori di validazione"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class StorageException(ChatbotException):
    """Eccezione per errori di storage"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "STORAGE_ERROR", details)

async def chatbot_exception_handler(request: Request, exc: ChatbotException):
    """Handler per le eccezioni del chatbot"""
    logger.error(f"Chatbot error: {exc.error_code} - {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler per errori di validazione Pydantic"""
    logger.warning(f"Validation error: {exc}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Dati di input non validi",
            "details": {
                "errors": exc.errors()
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler per eccezioni HTTP"""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {}
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handler generale per eccezioni non gestite"""
    logger.error(f"Unhandled error: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Si è verificato un errore interno del server",
            "details": {
                "type": type(exc).__name__
            }
        }
    )

def setup_exception_handlers(app: FastAPI) -> None:
    """Configura tutti gli handler di eccezioni"""
    app.add_exception_handler(ChatbotException, chatbot_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
