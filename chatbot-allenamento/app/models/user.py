"""
Modelli dati per gli utenti
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    """Ruoli utente"""
    USER = "user"
    ADMIN = "admin"
    TRAINER = "trainer"

class UserStatus(str, Enum):
    """Stati utente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserPreferences(BaseModel):
    """Preferenze utente"""
    language: str = Field(default="it", description="Lingua preferita")
    theme: str = Field(default="light", description="Tema interfaccia")
    notifications: bool = Field(default=True, description="Notifiche abilitate")
    workout_reminders: bool = Field(default=True, description="Promemoria allenamenti")
    privacy_level: str = Field(default="normal", description="Livello privacy")

class User(BaseModel):
    """Modello utente completo"""
    id: str = Field(..., description="ID univoco utente")
    email: Optional[str] = Field(default=None, description="Email utente")
    username: Optional[str] = Field(default=None, description="Nome utente")
    full_name: Optional[str] = Field(default=None, description="Nome completo")
    role: UserRole = Field(default=UserRole.USER, description="Ruolo utente")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Stato utente")
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="Preferenze")
    created_at: datetime = Field(default_factory=datetime.now, description="Data creazione")
    updated_at: datetime = Field(default_factory=datetime.now, description="Data aggiornamento")
    last_login: Optional[datetime] = Field(default=None, description="Ultimo accesso")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadati aggiuntivi")
    
    # Statistiche utente
    total_chats: int = Field(default=0, description="Numero totale chat")
    total_workouts: int = Field(default=0, description="Numero totale schede")
    total_messages: int = Field(default=0, description="Numero totale messaggi")
    
    def update_last_login(self) -> None:
        """Aggiorna timestamp ultimo accesso"""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()
    
    def increment_stats(self, chats: int = 0, workouts: int = 0, messages: int = 0) -> None:
        """Incrementa statistiche utente"""
        self.total_chats += chats
        self.total_workouts += workouts
        self.total_messages += messages
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Verifica se l'utente è attivo"""
        return self.status == UserStatus.ACTIVE
    
    def can_create_workout(self) -> bool:
        """Verifica se l'utente può creare schede"""
        return self.is_active() and self.role in [UserRole.USER, UserRole.TRAINER, UserRole.ADMIN]
