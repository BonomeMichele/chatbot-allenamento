"""
Schemi Pydantic per le API utente
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class UserCreateRequest(BaseModel):
    """Schema per creazione utente"""
    email: Optional[EmailStr] = Field(default=None, description="Email utente")
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, description="Nome utente")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Nome completo")

class UserUpdateRequest(BaseModel):
    """Schema per aggiornamento utente"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, description="Nome utente")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Nome completo")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Preferenze utente")

class UserResponse(BaseModel):
    """Schema per risposta utente"""
    id: str = Field(..., description="ID utente")
    email: Optional[str] = Field(default=None, description="Email utente")
    username: Optional[str] = Field(default=None, description="Nome utente")
    full_name: Optional[str] = Field(default=None, description="Nome completo")
    role: str = Field(..., description="Ruolo utente")
    status: str = Field(..., description="Stato utente")
    created_at: datetime = Field(..., description="Data creazione")
    last_login: Optional[datetime] = Field(default=None, description="Ultimo accesso")
    total_chats: int = Field(..., description="Numero totale chat")
    total_workouts: int = Field(..., description="Numero totale schede")
    total_messages: int = Field(..., description="Numero totale messaggi")

class UserStatsResponse(BaseModel):
    """Schema per statistiche utente"""
    total_chats: int = Field(..., description="Numero totale chat")
    total_workouts: int = Field(..., description="Numero totale schede")
    total_messages: int = Field(..., description="Numero totale messaggi")
    active_chats: int = Field(..., description="Chat attive")
    last_activity: Optional[datetime] = Field(default=None, description="Ultima attività")
