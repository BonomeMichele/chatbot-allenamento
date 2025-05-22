"""
Route API per gestione chat
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import (
    ChatMessageRequest, ChatResponse, ChatListResponse, 
    ChatDetailResponse, ChatDeleteResponse, ErrorResponse,
    ChatCreateRequest, ChatUpdateRequest
)
from app.dependencies import get_chat_service, get_workout_service
from app.services.chat_service import ChatService
from app.services.workout_service import WorkoutService
from app.core.error_handler import ChatbotException

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Invia un messaggio e riceve una risposta
    """
    try:
        # Verifica se è una richiesta di scheda di allenamento
        is_workout_request = chat_service.is_workout_request(request.message)
        
        if is_workout_request:
            # Genera una scheda di allenamento
            workout_plan = await workout_service.generate_workout_plan(
                user_input=request.message,
                chat_id=request.chat_id
            )
            
            # Formatta la scheda per la visualizzazione
            formatted_workout = workout_service.format_workout_for_display(workout_plan)
            
            # Crea un messaggio di risposta con la scheda
            chat, user_message, assistant_message = await chat_service.send_message(
                message_content=request.message,
                chat_id=request.chat_id
            )
            
            # Sovrascrivi il contenuto con la scheda formattata
            assistant_message.content = formatted_workout
            assistant_message.type = "workout"
            
            # Aggiorna la chat con il messaggio modificato
            chat.messages[-1] = assistant_message
            await chat_service.save_chat(chat)
            
        else:
            # Gestione normale della chat
            chat, user_message, assistant_message = await chat_service.send_message(
                message_content=request.message,
                chat_id=request.chat_id
            )
        
        return ChatResponse(
            chat_id=chat.id,
            title=chat.title,
            user_message={
                "message_id": user_message.id,
                "content": user_message.content,
                "type": user_message.type.value,
                "sources": user_message.sources,
                "timestamp": user_message.timestamp
            },
            assistant_message={
                "message_id": assistant_message.id,
                "content": assistant_message.content,
                "type": assistant_message.type.value,
                "sources": assistant_message.sources,
                "timestamp": assistant_message.timestamp
            }
        )
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.get("/chat/list", response_model=ChatListResponse)
async def list_chats(
    limit: int = 50,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Lista tutte le chat disponibili
    """
    try:
        chats = await chat_service.list_chats(limit=limit)
        
        return ChatListResponse(
            chats=[
                {
                    "id": chat["id"],
                    "title": chat["title"],
                    "last_message": chat.get("last_message"),
                    "created_at": chat["created_at"],
                    "updated_at": chat["updated_at"],
                    "message_count": chat["message_count"]
                }
                for chat in chats
            ],
            total=len(chats)
        )
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in list_chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in list_chats: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.get("/chat/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Ottiene i dettagli di una chat specifica
    """
    try:
        chat = await chat_service.get_chat(chat_id)
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat non trovata")
        
        return ChatDetailResponse(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages=[
                {
                    "message_id": msg.id,
                    "content": msg.content,
                    "type": msg.type.value,
                    "sources": msg.sources,
                    "timestamp": msg.timestamp
                }
                for msg in chat.messages
            ]
        )
        
    except HTTPException:
        raise
    except ChatbotException as e:
        logger.error(f"Chatbot error in get_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_chat: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.put("/chat/{chat_id}", response_model=dict)
async def update_chat(
    chat_id: str,
    request: ChatUpdateRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Aggiorna una chat (es. titolo)
    """
    try:
        if request.title:
            success = await chat_service.update_chat_title(chat_id, request.title)
            if not success:
                raise HTTPException(status_code=404, detail="Chat non trovata")
        
        return {"success": True, "message": "Chat aggiornata con successo"}
        
    except HTTPException:
        raise
    except ChatbotException as e:
        logger.error(f"Chatbot error in update_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_chat: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.delete("/chat/{chat_id}", response_model=ChatDeleteResponse)
async def delete_chat(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Elimina una chat specifica
    """
    try:
        success = await chat_service.delete_chat(chat_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat non trovata")
        
        return ChatDeleteResponse(
            success=True,
            message="Chat eliminata con successo",
            deleted_chat_id=chat_id
        )
        
    except HTTPException:
        raise
    except ChatbotException as e:
        logger.error(f"Chatbot error in delete_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_chat: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.delete("/chat", response_model=dict)
async def delete_all_chats(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Elimina tutte le chat
    """
    try:
        deleted_count = await chat_service.delete_all_chats()
        
        return {
            "success": True,
            "message": f"Eliminate {deleted_count} chat",
            "deleted_count": deleted_count
        }
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in delete_all_chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_all_chats: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.post("/chat", response_model=dict)
async def create_chat(
    request: ChatCreateRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Crea una nuova chat vuota
    """
    try:
        # Per ora, creiamo semplicemente una risposta che indica che la chat
        # verrà creata al primo messaggio
        return {
            "success": True,
            "message": "Nuova chat verrà creata al primo messaggio",
            "chat_id": None
        }
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in create_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_chat: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.get("/chat/stats", response_model=dict)
async def get_chat_statistics(
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Ottiene statistiche sulle chat
    """
    try:
        stats = await chat_service.get_chat_statistics()
        return stats
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in get_chat_statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_chat_statistics: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")
