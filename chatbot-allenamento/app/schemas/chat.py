"""
Schemi Pydantic per le API chat
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    """Schema per la richiesta di invio messaggio"""
    message: str = Field(..., min_length=1, max_length=5000, description="Contenuto del messaggio")
    chat_id: Optional[str] = Field(default=None, description="ID della chat esistente")

class ChatMessageResponse(BaseModel):
    """Schema per la risposta del messaggio"""
    message_id: str = Field(..., description="ID del messaggio generato")
    content: str = Field(..., description="Contenuto della risposta")
    type: str = Field(..., description="Tipo di messaggio")
    sources: Optional[List[str]] = Field(default=None, description="Fonti utilizzate")
    timestamp: datetime = Field(..., description="Timestamp della risposta")

class ChatResponse(BaseModel):
    """Schema per la risposta completa della chat"""
    chat_id: str = Field(..., description="ID della chat")
    title: str = Field(..., description="Titolo della chat")
    user_message: ChatMessageResponse = Field(..., description="Messaggio dell'utente")
    assistant_message: ChatMessageResponse = Field(..., description="Risposta dell'assistente")

class ChatListItem(BaseModel):
    """Schema per un elemento nella lista delle chat"""
    id: str = Field(..., description="ID della chat")
    title: str = Field(..., description="Titolo della chat")
    last_message: Optional[str] = Field(default=None, description="Ultimo messaggio")
    created_at: datetime = Field(..., description="Data di creazione")
    updated_at: datetime = Field(..., description="Data ultimo aggiornamento")
    message_count: int = Field(..., description="Numero di messaggi")

class ChatListResponse(BaseModel):
    """Schema per la lista delle chat"""
    chats: List[ChatListItem] = Field(..., description="Lista delle chat")
    total: int = Field(..., description="Numero totale di chat")

class ChatDetailResponse(BaseModel):
    """Schema per i dettagli di una chat"""
    id: str = Field(..., description="ID della chat")
    title: str = Field(..., description="Titolo della chat")
    created_at: datetime = Field(..., description="Data di creazione")
    updated_at: datetime = Field(..., description="Data ultimo aggiornamento")
    messages: List[ChatMessageResponse] = Field(..., description="Lista dei messaggi")

class ChatCreateRequest(BaseModel):
    """Schema per la creazione di una nuova chat"""
    title: Optional[str] = Field(default=None, description="Titolo della chat")

class ChatUpdateRequest(BaseModel):
    """Schema per l'aggiornamento di una chat"""
    title: Optional[str] = Field(default=None, description="Nuovo titolo della chat")

class ChatDeleteResponse(BaseModel):
    """Schema per la risposta di eliminazione chat"""
    success: bool = Field(..., description="Successo dell'operazione")
    message: str = Field(..., description="Messaggio di conferma")
    deleted_chat_id: str = Field(..., description="ID della chat eliminata")

class ErrorResponse(BaseModel):
    """Schema per le risposte di errore"""
    error: str = Field(..., description="Tipo di errore")
    message: str = Field(..., description="Messaggio di errore")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Dettagli aggiuntivi")
