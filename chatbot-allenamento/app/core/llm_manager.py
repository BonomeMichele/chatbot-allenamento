"""
Gestione interazioni con OpenAI
"""

import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.core.error_handler import LLMException

logger = logging.getLogger(__name__)

class LLMManager:
    """Gestore per le interazioni con OpenAI"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Genera una risposta utilizzando OpenAI
        
        Args:
            messages: Lista dei messaggi della conversazione
            system_prompt: Prompt di sistema opzionale
            temperature: Temperatura per la generazione
            max_tokens: Numero massimo di token
            
        Returns:
            Risposta generata dal modello
        """
        try:
            # Prepara i messaggi
            api_messages = []
            
            # Aggiungi system prompt se fornito
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            
            # Aggiungi i messaggi della conversazione
            api_messages.extend(messages)
            
            # Parametri per la chiamata API
            call_params = {
                "model": self.model,
                "messages": api_messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            logger.info(f"Generating response with {len(api_messages)} messages")
            
            # Chiamata API
            response = await self.client.chat.completions.create(**call_params)
            
            # Estrai la risposta
            content = response.choices[0].message.content
            
            if not content:
                raise LLMException("Il modello ha restituito una risposta vuota")
            
            logger.info("Response generated successfully")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            if "API key" in str(e).lower():
                raise LLMException("Chiave API OpenAI non valida o mancante")
            elif "rate limit" in str(e).lower():
                raise LLMException("Limite di rate raggiunto, riprova tra poco")
            elif "quota" in str(e).lower():
                raise LLMException("Quota API esaurita")
            else:
                raise LLMException(f"Errore nella generazione della risposta: {str(e)}")
    
    async def generate_workout_response(
        self,
        user_input: str,
        context: str,
        system_prompt: str
    ) -> str:
        """
        Genera una scheda di allenamento
        
        Args:
            user_input: Input dell'utente
            context: Contesto recuperato dal RAG
            system_prompt: Prompt di sistema specifico per workout
            
        Returns:
            Scheda di allenamento generata
        """
        messages = [
            {
                "role": "user",
                "content": f"""
Contesto dalle fonti documentali:
{context}

Richiesta dell'utente:
{user_input}

Genera una scheda di allenamento personalizzata basandoti sul contesto fornito e seguendo le linee guida italiane per il fitness.
"""
            }
        ]
        
        return await self.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3  # Temperatura bassa per maggiore coerenza
        )
    
    async def generate_chat_response(
        self,
        conversation_history: List[Dict[str, str]],
        context: str,
        system_prompt: str
    ) -> str:
        """
        Genera una risposta per la chat
        
        Args:
            conversation_history: Cronologia della conversazione
            context: Contesto recuperato dal RAG
            system_prompt: Prompt di sistema
            
        Returns:
            Risposta generata
        """
        # Aggiungi il contesto come messaggio di sistema aggiuntivo
        enhanced_messages = conversation_history.copy()
        
        # Se c'è contesto, aggiungilo al primo messaggio utente
        if context and enhanced_messages:
            last_user_msg = None
            for i, msg in enumerate(enhanced_messages):
                if msg["role"] == "user":
                    last_user_msg = i
            
            if last_user_msg is not None:
                original_content = enhanced_messages[last_user_msg]["content"]
                enhanced_messages[last_user_msg]["content"] = f"""
Contesto dalle fonti documentali:
{context}

{original_content}
"""
        
        return await self.generate_response(
            messages=enhanced_messages,
            system_prompt=system_prompt
        )
    
    async def extract_user_profile(self, user_input: str) -> Dict[str, Any]:
        """
        Estrae il profilo utente dall'input naturale
        
        Args:
            user_input: Input dell'utente in linguaggio naturale
            
        Returns:
            Dizionario con i parametri estratti
        """
        extraction_prompt = """
Analizza il seguente testo e estrai le informazioni dell'utente per generare una scheda di allenamento.

Restituisci SOLO un JSON valido con i seguenti campi (usa null per valori non specificati):
{
    "age": numero o null,
    "gender": "maschio", "femmina", "altro" o null,
    "experience_level": "principiante", "intermedio", "avanzato",
    "goals": array di stringhe tra ["forza", "ipertrofia", "resistenza", "dimagrimento", "fitness_generale"],
    "available_days": numero di giorni o null,
    "session_duration": durata in minuti o null,
    "injuries": array di stringhe con infortuni/limitazioni,
    "equipment": array di stringhe con attrezzature disponibili,
    "preferences": array di stringhe con preferenze
}
"""
        
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = await self.generate_response(
                messages=messages,
                system_prompt=extraction_prompt,
                temperature=0.1  # Temperatura molto bassa per output strutturato
            )
            
            # Prova a parsare il JSON
            import json
            return json.loads(response)
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse user profile JSON, using defaults")
            return {
                "age": None,
                "gender": None,
                "experience_level": "principiante",
                "goals": ["fitness_generale"],
                "available_days": 3,
                "session_duration": None,
                "injuries": [],
                "equipment": [],
                "preferences": []
            }
        except Exception as e:
            logger.error(f"Error extracting user profile: {e}")
            raise LLMException(f"Errore nell'estrazione del profilo utente: {str(e)}")
    
    def is_available(self) -> bool:
        """Verifica se il servizio LLM è disponibile"""
        return bool(settings.OPENAI_API_KEY)
