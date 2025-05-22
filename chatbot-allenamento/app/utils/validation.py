"""
Validazione input utente
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from app.models.workout import ExperienceLevel, WorkoutGoal, Gender
from app.core.error_handler import ValidationException

logger = logging.getLogger(__name__)

class InputValidator:
    """Validatore per input utente"""
    
    @staticmethod
    def validate_message_content(content: str) -> bool:
        """
        Valida il contenuto di un messaggio
        
        Args:
            content: Contenuto del messaggio
            
        Returns:
            True se valido
            
        Raises:
            ValidationException: Se non valido
        """
        if not content or not content.strip():
            raise ValidationException("Il messaggio non può essere vuoto")
        
        if len(content) > 5000:
            raise ValidationException("Il messaggio è troppo lungo (max 5000 caratteri)")
        
        # Verifica caratteri pericolosi/spam
        if InputValidator._contains_spam_patterns(content):
            raise ValidationException("Il messaggio contiene contenuto non consentito")
        
        return True
    
    @staticmethod
    def validate_workout_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una richiesta di generazione scheda
        
        Args:
            request_data: Dati della richiesta
            
        Returns:
            Dati validati e puliti
            
        Raises:
            ValidationException: Se non validi
        """
        validated = {}
        
        # Valida user_input
        user_input = request_data.get('user_input', '').strip()
        if not user_input:
            raise ValidationException("Input utente richiesto")
        
        if len(user_input) < 10:
            raise ValidationException("Descrivi meglio le tue esigenze (minimo 10 caratteri)")
        
        if len(user_input) > 2000:
            raise ValidationException("Descrizione troppo lunga (max 2000 caratteri)")
        
        validated['user_input'] = user_input
        
        # Valida parametri opzionali
        if 'age' in request_data:
            age = request_data['age']
            if age is not None:
                if not isinstance(age, int) or age < 12 or age > 100:
                    raise ValidationException("Età deve essere tra 12 e 100 anni")
                validated['age'] = age
        
        if 'available_days' in request_data:
            days = request_data['available_days']
            if days is not None:
                if not isinstance(days, int) or days < 1 or days > 7:
                    raise ValidationException("Giorni disponibili devono essere tra 1 e 7")
                validated['available_days'] = days
        
        # Valida experience_level
        if 'experience_level' in request_data:
            level = request_data['experience_level']
            if level:
                try:
                    ExperienceLevel(level)
                    validated['experience_level'] = level
                except ValueError:
                    raise ValidationException(f"Livello esperienza non valido: {level}")
        
        # Valida goals
        if 'goals' in request_data:
            goals = request_data['goals']
            if goals:
                if not isinstance(goals, list):
                    raise ValidationException("Gli obiettivi devono essere una lista")
                
                validated_goals = []
                for goal in goals:
                    try:
                        WorkoutGoal(goal)
                        validated_goals.append(goal)
                    except ValueError:
                        logger.warning(f"Obiettivo non valido ignorato: {goal}")
                
                if validated_goals:
                    validated['goals'] = validated_goals
        
        return validated
    
    @staticmethod
    def validate_user_profile_data(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida i dati del profilo utente estratti dal LLM
        
        Args:
            profile_data: Dati del profilo
            
        Returns:
            Dati validati
        """
        validated = {}
        
        # Età
        age = profile_data.get('age')
        if age is not None:
            if isinstance(age, (int, float)) and 12 <= age <= 100:
                validated['age'] = int(age)
        
        # Genere
        gender = profile_data.get('gender')
        if gender:
            try:
                Gender(gender.lower())
                validated['gender'] = gender.lower()
            except ValueError:
                pass
        
        # Livello esperienza
        experience = profile_data.get('experience_level', 'principiante')
        try:
            ExperienceLevel(experience)
            validated['experience_level'] = experience
        except ValueError:
            validated['experience_level'] = 'principiante'
        
        # Obiettivi
        goals = profile_data.get('goals', [])
        if isinstance(goals, list):
            validated_goals = []
            for goal in goals:
                try:
                    WorkoutGoal(goal)
                    validated_goals.append(goal)
                except ValueError:
                    continue
            validated['goals'] = validated_goals if validated_goals else ['fitness_generale']
        else:
            validated['goals'] = ['fitness_generale']
        
        # Giorni disponibili
        days = profile_data.get('available_days')
        if isinstance(days, (int, float)) and 1 <= days <= 7:
            validated['available_days'] = int(days)
        else:
            validated['available_days'] = 3
        
        # Durata sessione
        duration = profile_data.get('session_duration')
        if isinstance(duration, (int, float)) and 15 <= duration <= 180:
            validated['session_duration'] = int(duration)
        
        # Liste (injuries, equipment, preferences)
        for field in ['injuries', 'equipment', 'preferences']:
            value = profile_data.get(field, [])
            if isinstance(value, list):
                # Pulisci e valida ogni elemento
                cleaned = [
                    str(item).strip() 
                    for item in value 
                    if item and len(str(item).strip()) > 0
                ]
                validated[field] = cleaned[:10]  # Limita a 10 elementi
            else:
                validated[field] = []
        
        return validated
    
    @staticmethod
    def validate_chat_title(title: str) -> str:
        """
        Valida e pulisce il titolo di una chat
        
        Args:
            title: Titolo da validare
            
        Returns:
            Titolo validato
            
        Raises:
            ValidationException: Se non valido
        """
        if not title or not title.strip():
            raise ValidationException("Il titolo non può essere vuoto")
        
        cleaned_title = title.strip()
        
        if len(cleaned_title) > 100:
            cleaned_title = cleaned_title[:97] + "..."
        
        # Rimuovi caratteri pericolosi
        cleaned_title = re.sub(r'[<>\"\'&]', '', cleaned_title)
        
        return cleaned_title
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Valida un percorso file per sicurezza
        
        Args:
            file_path: Percorso da validare
            
        Returns:
            True se sicuro
        """
        # Blocca path traversal
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # Blocca caratteri pericolosi
        dangerous_chars = ['<', '>', '|', '&', ';', '$', '`']
        if any(char in file_path for char in dangerous_chars):
            return False
        
        return True
    
    @staticmethod
    def _contains_spam_patterns(content: str) -> bool:
        """
        Verifica se il contenuto contiene pattern di spam
        
        Args:
            content: Contenuto da verificare
            
        Returns:
            True se contiene spam
        """
        spam_patterns = [
            r'https?://[^\s]{10,}',  # URL molto lunghi
            r'[A-Z]{20,}',           # Troppo maiuscolo
            r'(.)\1{10,}',           # Caratteri ripetuti
            r'(buy now|click here|free money|viagra)',  # Spam comune
        ]
        
        content_lower = content.lower()
        
        for pattern in spam_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Pulisce un nome file rimuovendo caratteri pericolosi
        
        Args:
            filename: Nome file originale
            
        Returns:
            Nome file pulito
        """
        # Rimuovi caratteri pericolosi
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limita lunghezza
        if len(safe_name) > 100:
            name_part = safe_name[:90]
            ext_part = safe_name[-10:]
            safe_name = name_part + ext_part
        
        return safe_name
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """
        Valida e pulisce una query di ricerca
        
        Args:
            query: Query da validare
            
        Returns:
            Query validata
            
        Raises:
            ValidationException: Se non valida
        """
        if not query or not query.strip():
            raise ValidationException("Query di ricerca vuota")
        
        cleaned_query = query.strip()
        
        if len(cleaned_query) < 2:
            raise ValidationException("Query troppo corta (minimo 2 caratteri)")
        
        if len(cleaned_query) > 200:
            raise ValidationException("Query troppo lunga (max 200 caratteri)")
        
        # Rimuovi caratteri di controllo
        cleaned_query = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned_query)
        
        return cleaned_query
