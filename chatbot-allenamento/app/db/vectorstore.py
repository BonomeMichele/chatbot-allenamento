"""
Gestione del vectorstore per il sistema RAG
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import SimpleVectorStore
from app.config import settings
from app.core.error_handler import RAGException

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Gestore per il vector store"""
    
    def __init__(self):
        self.storage_path = settings.VECTOR_STORE_PATH
        self.index: Optional[VectorStoreIndex] = None
        self._ensure_storage_path()
    
    def _ensure_storage_path(self) -> None:
        """Assicura che il percorso di storage esista"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_index(self, index: VectorStoreIndex) -> None:
        """
        Salva l'indice nel vector store
        
        Args:
            index: Indice da salvare
        """
        try:
            self._ensure_storage_path()
            index.storage_context.persist(persist_dir=str(self.storage_path))
            self.index = index
            logger.info(f"Indice salvato in {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio dell'indice: {e}")
            raise RAGException(f"Errore nel salvataggio dell'indice: {str(e)}")
    
    def load_index(self) -> Optional[VectorStoreIndex]:
        """
        Carica l'indice dal vector store
        
        Returns:
            Indice caricato o None se non esistente
        """
        try:
            # Verifica se esistono file di indice
            if not self._index_exists():
                logger.info("Nessun indice esistente trovato")
                return None
            
            # Carica il contesto di storage
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.storage_path)
            )
            
            # Carica l'indice
            index = load_index_from_storage(storage_context)
            self.index = index
            
            logger.info(f"Indice caricato da {self.storage_path}")
            return index
            
        except Exception as e:
            logger.error(f"Errore nel caricamento dell'indice: {e}")
            return None
    
    def _index_exists(self) -> bool:
        """
        Verifica se esiste un indice salvato
        
        Returns:
            True se l'indice esiste
        """
        try:
            # Controlla i file tipici di un indice LlamaIndex
            required_files = [
                "docstore.json",
                "index_store.json", 
                "vector_store.json"
            ]
            
            for filename in required_files:
                if not (self.storage_path / filename).exists():
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Errore nella verifica esistenza indice: {e}")
            return False
    
    def delete_index(self) -> bool:
        """
        Elimina l'indice dal vector store
        
        Returns:
            True se eliminato con successo
        """
        try:
            if self.storage_path.exists():
                import shutil
                shutil.rmtree(self.storage_path)
                self.storage_path.mkdir(parents=True, exist_ok=True)
                self.index = None
                logger.info("Indice eliminato con successo")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Errore nell'eliminazione dell'indice: {e}")
            raise RAGException(f"Errore nell'eliminazione dell'indice: {str(e)}")
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Ottiene informazioni sull'indice
        
        Returns:
            Dizionario con informazioni sull'indice
        """
        try:
            info = {
                'exists': self._index_exists(),
                'storage_path': str(self.storage_path),
                'loaded': self.index is not None
            }
            
            if self._index_exists():
                # Calcola dimensione storage
                total_size = sum(
                    f.stat().st_size 
                    for f in self.storage_path.rglob('*') 
                    if f.is_file()
                )
                info['size_bytes'] = total_size
                info['size_mb'] = round(total_size / (1024 * 1024), 2)
                
                # Conta file
                info['total_files'] = len(list(self.storage_path.rglob('*')))
            
            return info
            
        except Exception as e:
            logger.error(f"Errore nel recupero info indice: {e}")
            return {'error': str(e)}
    
    def backup_index(self, backup_path: Path) -> bool:
        """
        Crea un backup dell'indice
        
        Args:
            backup_path: Percorso dove salvare il backup
            
        Returns:
            True se backup creato con successo
        """
        try:
            if not self._index_exists():
                logger.warning("Nessun indice da backuppare")
                return False
            
            import shutil
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copia tutti i file dell'indice
            for item in self.storage_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, backup_path / item.name)
                elif item.is_dir():
                    shutil.copytree(item, backup_path / item.name, dirs_exist_ok=True)
            
            logger.info(f"Backup indice creato in {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Errore nella creazione backup: {e}")
            raise RAGException(f"Errore nella creazione backup: {str(e)}")
    
    def restore_index(self, backup_path: Path) -> bool:
        """
        Ripristina l'indice da un backup
        
        Args:
            backup_path: Percorso del backup
            
        Returns:
            True se ripristino completato con successo
        """
        try:
            if not backup_path.exists():
                raise RAGException(f"Backup non trovato in {backup_path}")
            
            # Elimina l'indice corrente
            self.delete_index()
            
            import shutil
            
            # Ripristina i file dal backup
            for item in backup_path.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.storage_path / item.name)
                elif item.is_dir():
                    shutil.copytree(item, self.storage_path / item.name)
            
            # Prova a caricare l'indice ripristinato
            restored_index = self.load_index()
            if restored_index:
                logger.info(f"Indice ripristinato da {backup_path}")
                return True
            else:
                raise RAGException("Indice ripristinato non valido")
            
        except Exception as e:
            logger.error(f"Errore nel ripristino indice: {e}")
            raise RAGException(f"Errore nel ripristino indice: {str(e)}")
    
    def optimize_index(self) -> bool:
        """
        Ottimizza l'indice (placeholder per future implementazioni)
        
        Returns:
            True se ottimizzazione completata
        """
        try:
            if not self.index:
                logger.warning("Nessun indice caricato da ottimizzare")
                return False
            
            # TODO: Implementare ottimizzazioni specifiche se necessarie
            # Ad esempio: rimozione duplicati, compattazione, ecc.
            
            logger.info("Ottimizzazione indice completata")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'ottimizzazione indice: {e}")
            return False
    
    def get_current_index(self) -> Optional[VectorStoreIndex]:
        """
        Ottiene l'indice correntemente caricato
        
        Returns:
            Indice corrente o None
        """
        return self.index
    
    def is_index_loaded(self) -> bool:
        """
        Verifica se un indice è caricato in memoria
        
        Returns:
            True se indice caricato
        """
        return self.index is not None
