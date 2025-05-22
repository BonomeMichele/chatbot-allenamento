"""
Servizio per gestione chat
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from app.models.chat import Chat, Message, MessageRole, MessageType
from app.db.file_storage import FileStorage
from app.core.llm_manager import LLMManager
from app.core.rag_engine import RAGEngine
from app.utils.prompt_templates import PromptTemplates
from app.core.error_handler import ChatbotException

logger = logging.getLogger(__name__)

class ChatService:
    """Servizio per la gestione delle chat"""
    
    def __init__(self, storage: FileStorage, llm_manager: LLMManager, rag_engine: RAGEngine):
        self.storage = storage
        self.llm_manager = llm_manager
        self.rag_engine = rag_engine
        self.prompt_templates = PromptTemplates()
    
    async def send_message(self, message_content: str, chat_id: Optional[str] = None) -> Tuple[Chat, Message, Message]:
        """
        Invia un messaggio e riceve una risposta
        
        Args:
            message_content: Contenuto del messaggio dell'utente
            chat_id: ID della chat esistente (None per nuova chat)
            
        Returns:
            Tupla (chat, messaggio_utente, messaggio_assistente)
        """
        try:
            # Carica o crea la chat
            if chat_id:
                chat = await self.get_chat(chat_id)
                if not chat:
                    raise ChatbotException(f"Chat {chat_id} non trovata")
            else:
                chat = self._create_new_chat()
            
            # Crea il messaggio dell'utente
            user_message = Message(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=message_content,
                type=MessageType.TEXT
            )
            
            # Aggiungi il messaggio alla chat
            chat.add_message(user_message)
            
            # Genera la risposta
            assistant_message = await self._generate_response(chat, message_content)
            
            # Aggiungi la risposta alla chat
            chat.add_message(assistant_message)
            
            # Salva la chat
            await self.save_chat(chat)
            
            logger.info(f"Messaggio elaborato per chat {chat.id}")
            return chat, user_message, assistant_message
            
        except Exception as e:
            logger.error(f"Errore nell'elaborazione del messaggio: {e}")
            raise ChatbotException(f"Errore nell'elaborazione del messaggio: {str(e)}")
    
    async def _generate_response(self, chat: Chat, user_message: str) -> Message:
        """
        Genera una risposta dell'assistente
        
        Args:
            chat: Chat corrente
            user_message: Messaggio dell'utente
            
        Returns:
            Messaggio di risposta dell'assistente
        """
        try:
            # Recupera il contesto dal RAG
            context, sources = await self.rag_engine.retrieve_context(user_message)
            
            # Ottieni la cronologia della conversazione
            conversation_history = chat.get_conversation_history(limit=10)
            
            # Genera la risposta
            system_prompt = self.prompt_templates.get_chat_system_prompt()
            
            response_content = await self.llm_manager.generate_chat_response(
                conversation_history=conversation_history,
                context=context,
                system_prompt=system_prompt
            )
            
            # Crea il messaggio di risposta
            assistant_message = Message(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=response_content,
                type=MessageType.TEXT,
                sources=sources if sources else None
            )
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Errore nella generazione della risposta: {e}")
            
            # Messaggio di errore per l'utente
            error_message = Message(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content="Mi dispiace, si è verificato un errore nella generazione della risposta. Riprova tra poco.",
                type=MessageType.ERROR
            )
            
            return error_message
    
    def _create_new_chat(self) -> Chat:
        """
        Crea una nuova chat
        
        Returns:
            Nuova istanza di chat
        """
        chat_id = str(uuid.uuid4())
        
        chat = Chat(
            id=chat_id,
            title="Nuova Chat",
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return chat
    
    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        """
        Recupera una chat per ID
        
        Args:
            chat_id: ID della chat
            
        Returns:
            Chat trovata o None
        """
        try:
            chat_data = self.storage.load_chat(chat_id)
            if not chat_data:
                return None
            
            # Converti i dati in oggetto Chat
            messages = []
            for msg_data in chat_data.get('messages', []):
                message = Message(**msg_data)
                messages.append(message)
            
            chat = Chat(
                id=chat_data['id'],
                title=chat_data['title'],
                messages=messages,
                status=chat_data.get('status', 'active'),
                created_at=chat_data['created_at'],
                updated_at=chat_data['updated_at'],
                user_id=chat_data.get('user_id'),
                metadata=chat_data.get('metadata')
            )
            
            return chat
            
        except Exception as e:
            logger.error(f"Errore nel recupero della chat {chat_id}: {e}")
            return None
    
    async def save_chat(self, chat: Chat) -> None:
        """
        Salva una chat
        
        Args:
            chat: Chat da salvare
        """
        try:
            # Converti in dizionario
            chat_data = {
                'id': chat.id,
                'title': chat.title,
                'messages': [msg.model_dump() for msg in chat.messages],
                'status': chat.status,
                'created_at': chat.created_at,
                'updated_at': chat.updated_at,
                'user_id': chat.user_id,
                'metadata': chat.metadata
            }
            
            self.storage.save_chat(chat_data)
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio della chat {chat.id}: {e}")
            raise ChatbotException(f"Errore nel salvataggio della chat: {str(e)}")
    
    async def list_chats(self, limit: Optional[int] = None) -> List[dict]:
        """
        Lista tutte le chat
        
        Args:
            limit: Numero massimo di chat da restituire
            
        Returns:
            Lista delle chat
        """
        try:
            return self.storage.list_chats(limit=limit)
        except Exception as e:
            logger.error(f"Errore nell'elenco delle chat: {e}")
            raise ChatbotException(f"Errore nell'elenco delle chat: {str(e)}")
    
    async def delete_chat(self, chat_id: str) -> bool:
        """
        Elimina una chat
        
        Args:
            chat_id: ID della chat da eliminare
            
        Returns:
            True se eliminata con successo
        """
        try:
            return self.storage.delete_chat(chat_id)
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della chat {chat_id}: {e}")
            raise ChatbotException(f"Errore nell'eliminazione della chat: {str(e)}")
    
    async def delete_all_chats(self) -> int:
        """
        Elimina tutte le chat
        
        Returns:
            Numero di chat eliminate
        """
        try:
            return self.storage.delete_all_chats()
        except Exception as e:
            logger.error(f"Errore nell'eliminazione di tutte le chat: {e}")
            raise ChatbotException(f"Errore nell'eliminazione delle chat: {str(e)}")
    
    async def update_chat_title(self, chat_id: str, new_title: str) -> bool:
        """
        Aggiorna il titolo di una chat
        
        Args:
            chat_id: ID della chat
            new_title: Nuovo titolo
            
        Returns:
            True se aggiornato con successo
        """
        try:
            chat = await self.get_chat(chat_id)
            if not chat:
                return False
            
            chat.title = new_title
            chat.updated_at = datetime.now()
            
            await self.save_chat(chat)
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento del titolo della chat {chat_id}: {e}")
            raise ChatbotException(f"Errore nell'aggiornamento del titolo: {str(e)}")
    
    async def get_chat_statistics(self) -> dict:
        """
        Ottiene statistiche sulle chat
        
        Returns:
            Dizionario con le statistiche
        """
        try:
            chats = await self.list_chats()
            
            if not chats:
                return {
                    'total_chats': 0,
                    'total_messages': 0,
                    'average_messages_per_chat': 0,
                    'most_recent': None,
                    'oldest': None
                }
            
            total_messages = sum(chat.get('message_count', 0) for chat in chats)
            average_messages = total_messages / len(chats) if chats else 0
            
            # Ordina per data per trovare più recente e più vecchia
            sorted_chats = sorted(chats, key=lambda x: x.get('created_at', ''))
            
            return {
                'total_chats': len(chats),
                'total_messages': total_messages,
                'average_messages_per_chat': round(average_messages, 2),
                'most_recent': sorted_chats[-1] if sorted_chats else None,
                'oldest': sorted_chats[0] if sorted_chats else None
            }
            
        except Exception as e:
            logger.error(f"Errore nel calcolo delle statistiche: {e}")
            return {'error': str(e)}
    
    def is_workout_request(self, message: str) -> bool:
        """
        Determina se un messaggio è una richiesta di scheda di allenamento
        
        Args:
            message: Messaggio da analizzare
            
        Returns:
            True se è una richiesta di workout
        """
        workout_keywords = [
            'scheda', 'allenamento', 'workout', 'palestra', 'esercizi',
            'programma', 'routine', 'training', 'massa', 'forza',
            'definizione', 'dimagrimento', 'bodybuilding', 'fitness'
        ]
        
        message_lower = message.lower()
        
        # Verifica se contiene parole chiave di allenamento
        has_workout_keywords = any(keyword in message_lower for keyword in workout_keywords)
        
        # Verifica se contiene richieste dirette
        request_phrases = [
            'voglio allenarmi', 'come mi alleno', 'che esercizi',
            'scheda per', 'programma di', 'routine di'
        ]
        
        has_request_phrases = any(phrase in message_lower for phrase in request_phrases)
        
        return has_workout_keywords or has_request_phrases
