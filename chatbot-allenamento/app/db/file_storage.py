"""
Persistenza basata su file JSON
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from app.config import settings
from app.core.error_handler import StorageException

logger = logging.getLogger(__name__)

class FileStorage:
    """Gestore per la persistenza su file JSON"""
    
    def __init__(self):
        self.chats_path = settings.CHATS_PATH
        self.workouts_path = settings.WORKOUTS_PATH
        
        # Assicurati che le directory esistano
        self.chats_path.mkdir(parents=True, exist_ok=True)
        self.workouts_path.mkdir(parents=True, exist_ok=True)
    
    # === GESTIONE CHAT ===
    
    def save_chat(self, chat_data: Dict[str, Any]) -> None:
        """
        Salva una chat su file
        
        Args:
            chat_data: Dati della chat da salvare
        """
        try:
            chat_id = chat_data['id']
            file_path = self.chats_path / f"{chat_id}.json"
            
            # Converti datetime in string per la serializzazione
            serializable_data = self._prepare_for_json(chat_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Chat {chat_id} salvata con successo")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio della chat {chat_data.get('id')}: {e}")
            raise StorageException(f"Errore nel salvataggio della chat: {str(e)}")
    
    def load_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Carica una chat da file
        
        Args:
            chat_id: ID della chat da caricare
            
        Returns:
            Dati della chat o None se non trovata
        """
        try:
            file_path = self.chats_path / f"{chat_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converti le stringhe datetime in oggetti datetime
            return self._restore_from_json(data)
            
        except Exception as e:
            logger.error(f"Errore nel caricamento della chat {chat_id}: {e}")
            raise StorageException(f"Errore nel caricamento della chat: {str(e)}")
    
    def list_chats(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista tutte le chat disponibili
        
        Args:
            limit: Numero massimo di chat da restituire
            
        Returns:
            Lista delle chat ordinate per data di aggiornamento
        """
        try:
            chats = []
            
            for file_path in self.chats_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                    
                    # Aggiungi informazioni di base per la lista
                    chat_info = {
                        'id': chat_data.get('id'),
                        'title': chat_data.get('title', 'Chat senza titolo'),
                        'created_at': chat_data.get('created_at'),
                        'updated_at': chat_data.get('updated_at'),
                        'message_count': len(chat_data.get('messages', []))
                    }
                    
                    # Ultimo messaggio
                    messages = chat_data.get('messages', [])
                    if messages:
                        last_message = messages[-1]
                        chat_info['last_message'] = last_message.get('content', '')[:100]
                    
                    chats.append(chat_info)
                    
                except Exception as e:
                    logger.warning(f"Errore nel caricamento della chat {file_path.name}: {e}")
            
            # Ordina per data di aggiornamento (più recenti prima)
            chats.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Applica il limite se specificato
            if limit:
                chats = chats[:limit]
            
            return chats
            
        except Exception as e:
            logger.error(f"Errore nell'elenco delle chat: {e}")
            raise StorageException(f"Errore nell'elenco delle chat: {str(e)}")
    
    def delete_chat(self, chat_id: str) -> bool:
        """
        Elimina una chat
        
        Args:
            chat_id: ID della chat da eliminare
            
        Returns:
            True se eliminata con successo, False se non trovata
        """
        try:
            file_path = self.chats_path / f"{chat_id}.json"
            
            if not file_path.exists():
                return False
            
            file_path.unlink()
            logger.info(f"Chat {chat_id} eliminata con successo")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della chat {chat_id}: {e}")
            raise StorageException(f"Errore nell'eliminazione della chat: {str(e)}")
    
    def delete_all_chats(self) -> int:
        """
        Elimina tutte le chat
        
        Returns:
            Numero di chat eliminate
        """
        try:
            count = 0
            for file_path in self.chats_path.glob("*.json"):
                file_path.unlink()
                count += 1
            
            logger.info(f"Eliminate {count} chat")
            return count
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione di tutte le chat: {e}")
            raise StorageException(f"Errore nell'eliminazione delle chat: {str(e)}")
    
    # === GESTIONE SCHEDE ALLENAMENTO ===
    
    def save_workout(self, workout_data: Dict[str, Any]) -> None:
        """
        Salva una scheda di allenamento
        
        Args:
            workout_data: Dati della scheda da salvare
        """
        try:
            workout_id = workout_data['id']
            file_path = self.workouts_path / f"{workout_id}.json"
            
            # Converti datetime in string
            serializable_data = self._prepare_for_json(workout_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Scheda {workout_id} salvata con successo")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio della scheda {workout_data.get('id')}: {e}")
            raise StorageException(f"Errore nel salvataggio della scheda: {str(e)}")
    
    def load_workout(self, workout_id: str) -> Optional[Dict[str, Any]]:
        """
        Carica una scheda di allenamento
        
        Args:
            workout_id: ID della scheda da caricare
            
        Returns:
            Dati della scheda o None se non trovata
        """
        try:
            file_path = self.workouts_path / f"{workout_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._restore_from_json(data)
            
        except Exception as e:
            logger.error(f"Errore nel caricamento della scheda {workout_id}: {e}")
            raise StorageException(f"Errore nel caricamento della scheda: {str(e)}")
    
    def list_workouts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista tutte le schede disponibili
        
        Args:
            limit: Numero massimo di schede da restituire
            
        Returns:
            Lista delle schede ordinate per data di creazione
        """
        try:
            workouts = []
            
            for file_path in self.workouts_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        workout_data = json.load(f)
                    
                    # Informazioni di base per la lista
                    workout_info = {
                        'id': workout_data.get('id'),
                        'title': workout_data.get('title', 'Scheda senza titolo'),
                        'created_at': workout_data.get('created_at'),
                        'total_days': len(workout_data.get('workout_days', [])),
                        'total_exercises': sum(
                            len(day.get('exercises', []))
                            for day in workout_data.get('workout_days', [])
                        )
                    }
                    
                    workouts.append(workout_info)
                    
                except Exception as e:
                    logger.warning(f"Errore nel caricamento della scheda {file_path.name}: {e}")
            
            # Ordina per data di creazione (più recenti prima)
            workouts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Applica il limite se specificato
            if limit:
                workouts = workouts[:limit]
            
            return workouts
            
        except Exception as e:
            logger.error(f"Errore nell'elenco delle schede: {e}")
            raise StorageException(f"Errore nell'elenco delle schede: {str(e)}")
    
    def delete_workout(self, workout_id: str) -> bool:
        """
        Elimina una scheda di allenamento
        
        Args:
            workout_id: ID della scheda da eliminare
            
        Returns:
            True se eliminata con successo, False se non trovata
        """
        try:
            file_path = self.workouts_path / f"{workout_id}.json"
            
            if not file_path.exists():
                return False
            
            file_path.unlink()
            logger.info(f"Scheda {workout_id} eliminata con successo")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della scheda {workout_id}: {e}")
            raise StorageException(f"Errore nell'eliminazione della scheda: {str(e)}")
    
    # === UTILITÀ ===
    
    def _prepare_for_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara i dati per la serializzazione JSON convertendo datetime in stringhe
        
        Args:
            data: Dati da preparare
            
        Returns:
            Dati preparati per JSON
        """
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        return convert_datetime(data)
    
    def _restore_from_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ripristina i dati dal JSON convertendo le stringhe datetime
        
        Args:
            data: Dati da ripristinare
            
        Returns:
            Dati ripristinati
        """
        def restore_datetime(obj):
            if isinstance(obj, str):
                # Prova a convertire le stringhe che sembrano datetime
                if 'T' in obj and (obj.endswith('Z') or '+' in obj[-6:] or obj.count(':') >= 2):
                    try:
                        return datetime.fromisoformat(obj.replace('Z', '+00:00'))
                    except ValueError:
                        return obj
                return obj
            elif isinstance(obj, dict):
                return {k: restore_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [restore_datetime(item) for item in obj]
            else:
                return obj
        
        return restore_datetime(data)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sullo storage
        
        Returns:
            Dizionario con le statistiche
        """
        try:
            chat_files = list(self.chats_path.glob("*.json"))
            workout_files = list(self.workouts_path.glob("*.json"))
            
            # Calcola le dimensioni
            chat_size = sum(f.stat().st_size for f in chat_files)
            workout_size = sum(f.stat().st_size for f in workout_files)
            
            return {
                'chats': {
                    'count': len(chat_files),
                    'size_bytes': chat_size,
                    'size_mb': round(chat_size / (1024 * 1024), 2)
                },
                'workouts': {
                    'count': len(workout_files),
                    'size_bytes': workout_size,
                    'size_mb': round(workout_size / (1024 * 1024), 2)
                },
                'total': {
                    'files': len(chat_files) + len(workout_files),
                    'size_bytes': chat_size + workout_size,
                    'size_mb': round((chat_size + workout_size) / (1024 * 1024), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Errore nel calcolo delle statistiche: {e}")
            return {
                'error': str(e),
                'chats': {'count': 0, 'size_bytes': 0, 'size_mb': 0},
                'workouts': {'count': 0, 'size_bytes': 0, 'size_mb': 0},
                'total': {'files': 0, 'size_bytes': 0, 'size_mb': 0}
            }
    
    def cleanup_old_files(self, days: int = 30) -> Dict[str, int]:
        """
        Pulisce i file più vecchi di X giorni
        
        Args:
            days: Numero di giorni dopo i quali considerare i file vecchi
            
        Returns:
            Dizionario con il numero di file eliminati
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cleaned = {'chats': 0, 'workouts': 0}
            
            # Pulisci chat vecchie
            for file_path in self.chats_path.glob("*.json"):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    cleaned['chats'] += 1
            
            # Pulisci schede vecchie
            for file_path in self.workouts_path.glob("*.json"):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    cleaned['workouts'] += 1
            
            logger.info(f"Pulizia completata: {cleaned['chats']} chat e {cleaned['workouts']} schede eliminate")
            return cleaned
            
        except Exception as e:
            logger.error(f"Errore nella pulizia dei file: {e}")
            raise StorageException(f"Errore nella pulizia dei file: {str(e)}")
    
    def backup_data(self, backup_path: Path) -> bool:
        """
        Crea un backup di tutti i dati
        
        Args:
            backup_path: Percorso dove salvare il backup
            
        Returns:
            True se backup creato con successo
        """
        try:
            import shutil
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup chat
            chat_backup = backup_path / "chats"
            if self.chats_path.exists():
                shutil.copytree(self.chats_path, chat_backup, dirs_exist_ok=True)
            
            # Backup schede
            workout_backup = backup_path / "workouts"
            if self.workouts_path.exists():
                shutil.copytree(self.workouts_path, workout_backup, dirs_exist_ok=True)
            
            logger.info(f"Backup creato con successo in {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione del backup: {e}")
            raise StorageException(f"Errore nella creazione del backup: {str(e)}")
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        Ripristina i dati da un backup
        
        Args:
            backup_path: Percorso del backup da ripristinare
            
        Returns:
            True se ripristino completato con successo
        """
        try:
            import shutil
            
            if not backup_path.exists():
                raise StorageException(f"Backup non trovato in {backup_path}")
            
            # Ripristina chat
            chat_backup = backup_path / "chats"
            if chat_backup.exists():
                if self.chats_path.exists():
                    shutil.rmtree(self.chats_path)
                shutil.copytree(chat_backup, self.chats_path)
            
            # Ripristina schede
            workout_backup = backup_path / "workouts"
            if workout_backup.exists():
                if self.workouts_path.exists():
                    shutil.rmtree(self.workouts_path)
                shutil.copytree(workout_backup, self.workouts_path)
            
            logger.info(f"Ripristino completato da {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Errore nel ripristino dal backup: {e}")
            raise StorageException(f"Errore nel ripristino dal backup: {str(e)}")
