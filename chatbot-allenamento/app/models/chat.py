"""
Modelli dati per le chat
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class MessageRole(str, Enum):
    """Ruoli dei messaggi"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    """Tipi di messaggio"""
    TEXT = "text"
    WORKOUT = "workout"
    ERROR = "error"

class Message(BaseModel):
    """Modello per un singolo messaggio"""
    id: str = Field(..., description="ID univoco del messaggio")
    role: MessageRole = Field(..., description="Ruolo del mittente")
    content: str = Field(..., description="Contenuto del messaggio")
    type: MessageType = Field(default=MessageType.TEXT, description="Tipo di messaggio")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del messaggio")
    sources: Optional[List[str]] = Field(default=None, description="Fonti utilizzate per la risposta")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadati aggiuntivi")

class ChatStatus(str, Enum):
    """Stati della chat"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Chat(BaseModel):
    """Modello per una chat completa"""
    id: str = Field(..., description="ID univoco della chat")
    title: str = Field(..., description="Titolo della chat")
    messages: List[Message] = Field(default_factory=list, description="Lista dei messaggi")
    status: ChatStatus = Field(default=ChatStatus.ACTIVE, description="Stato della chat")
    created_at: datetime = Field(default_factory=datetime.now, description="Data di creazione")
    updated_at: datetime = Field(default_factory=datetime.now, description="Data ultimo aggiornamento")
    user_id: Optional[str] = Field(default=None, description="ID dell'utente (per future implementazioni)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadati aggiuntivi")
    
    def add_message(self, message: Message) -> None:
        """Aggiunge un messaggio alla chat"""
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # Aggiorna il titolo se è il primo messaggio utente
        if len(self.messages) == 1 and message.role == MessageRole.USER:
            self.title = message.content[:50] + ("..." if len(message.content) > 50 else "")
    
    def get_last_message(self) -> Optional[Message]:
        """Ottiene l'ultimo messaggio della chat"""
        return self.messages[-1] if self.messages else None
    
    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """Ottiene tutti i messaggi di un determinato ruolo"""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Ottiene la cronologia della conversazione in formato OpenAI"""
        messages = self.messages[-limit:] if limit else self.messages
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]
        ]
