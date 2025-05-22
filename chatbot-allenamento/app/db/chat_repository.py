"""
Repository per operazioni su chat
"""

import logging
from typing import List, Optional, Dict, Any
from app.db.file_storage import FileStorage
from app.models.chat import Chat
from app.core.error_handler import StorageException

logger = logging.getLogger(__name__)

class ChatRepository:
    """Repository per gestione chat"""
    
    def __init__(self, storage: FileStorage):
        self.storage = storage
    
    async def save(self, chat: Chat) -> None:
        """
        Salva una chat
        
        Args:
            chat: Chat da salvare
        """
        try:
            chat_data = {
                'id': chat.id,
                'title': chat.title,
                'messages': [msg.model_dump() for msg in chat.messages],
                'status': chat.status.value,
                'created_at': chat.created_at,
                'updated_at': chat.updated_at,
                'user_id': chat.user_id,
                'metadata': chat.metadata
            }
            
            self.storage.save_chat(chat_data)
            logger.info(f"Chat {chat.id} salvata nel repository")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio chat {chat.id}: {e}")
            raise StorageException(f"Errore nel salvataggio chat: {str(e)}")
    
    async def find_by_id(self, chat_id: str) -> Optional[Chat]:
        """
        Trova una chat per ID
        
        Args:
            chat_id: ID della chat
            
        Returns:
            Chat trovata o None
        """
        try:
            chat_data = self.storage.load_chat(chat_id)
            if not chat_data:
                return None
            
            # Converti in oggetto Chat
            from app.models.chat import Message, MessageRole, MessageType, ChatStatus
            
            messages = []
            for msg_data in chat_data.get('messages', []):
                message = Message(
                    id=msg_data['id'],
                    role=MessageRole(msg_data['role']),
                    content=msg_data['content'],
                    type=MessageType(msg_data.get('type', 'text')),
                    timestamp=msg_data['timestamp'],
                    sources=msg_data.get('sources'),
                    metadata=msg_data.get('metadata')
                )
                messages.append(message)
            
            chat = Chat(
                id=chat_data['id'],
                title=chat_data['title'],
                messages=messages,
                status=ChatStatus(chat_data.get('status', 'active')),
                created_at=chat_data['created_at'],
                updated_at=chat_data['updated_at'],
                user_id=chat_data.get('user_id'),
                metadata=chat_data.get('metadata')
            )
            
            return chat
            
        except Exception as e:
            logger.error(f"Errore nel recupero chat {chat_id}: {e}")
            return None
    
    async def find_all(self, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Trova tutte le chat
        
        Args:
            limit: Numero massimo di chat
            user_id: Filtra per utente specifico
            
        Returns:
            Lista delle chat
        """
        try:
            chats = self.storage.list_chats(limit=limit)
            
            # Filtra per user_id se specificato
            if user_id:
                filtered_chats = []
                for chat_info in chats:
                    chat_data = self.storage.load_chat(chat_info['id'])
                    if chat_data and chat_data.get('user_id') == user_id:
                        filtered_chats.append(chat_info)
                return filtered_chats
            
            return chats
            
        except Exception as e:
            logger.error(f"Errore nel recupero lista chat: {e}")
            raise StorageException(f"Errore nel recupero lista chat: {str(e)}")
    
    async def delete(self, chat_id: str) -> bool:
        """
        Elimina una chat
        
        Args:
            chat_id: ID della chat da eliminare
            
        Returns:
            True se eliminata con successo
        """
        try:
            result = self.storage.delete_chat(chat_id)
            if result:
                logger.info(f"Chat {chat_id} eliminata dal repository")
            return result
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione chat {chat_id}: {e}")
            raise StorageException(f"Errore nell'eliminazione chat: {str(e)}")
    
    async def delete_all(self, user_id: Optional[str] = None) -> int:
        """
        Elimina tutte le chat
        
        Args:
            user_id: Se specificato, elimina solo le chat dell'utente
            
        Returns:
            Numero di chat eliminate
        """
        try:
            if user_id:
                # Elimina solo le chat dell'utente specifico
                chats = await self.find_all(user_id=user_id)
                count = 0
                for chat_info in chats:
                    if await self.delete(chat_info['id']):
                        count += 1
                return count
            else:
                # Elimina tutte le chat
                return self.storage.delete_all_chats()
                
        except Exception as e:
            logger.error(f"Errore nell'eliminazione di tutte le chat: {e}")
            raise StorageException(f"Errore nell'eliminazione delle chat: {str(e)}")
    
    async def count(self, user_id: Optional[str] = None) -> int:
        """
        Conta il numero di chat
        
        Args:
            user_id: Se specificato, conta solo le chat dell'utente
            
        Returns:
            Numero di chat
        """
        try:
            chats = await self.find_all(user_id=user_id)
            return len(chats)
            
        except Exception as e:
            logger.error(f"Errore nel conteggio chat: {e}")
            return 0
    
    async def find_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Trova le chat di un utente specifico
        
        Args:
            user_id: ID dell'utente
            limit: Numero massimo di chat
            
        Returns:
            Lista delle chat dell'utente
        """
        return await self.find_all(limit=limit, user_id=user_id)
