"""
Funzionalità di embedding e indicizzazione
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PDFReader, DocxReader
from app.config import settings
from app.core.error_handler import RAGException

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Gestore per gli embeddings e l'indicizzazione"""
    
    def __init__(self):
        # Configura llama-index
        Settings.llm = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )
        
        Settings.embed_model = OpenAIEmbedding(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        
        # Configura il parser dei nodi
        self.node_parser = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Lettori per diversi formati
        self.readers = {
            '.pdf': PDFReader(),
            '.docx': DocxReader(),
        }
        
        self.index: Optional[VectorStoreIndex] = None
        self.documents: List[Document] = []
    
    def load_documents_from_directory(self, directory_path: Path) -> List[Document]:
        """
        Carica tutti i documenti supportati da una directory
        
        Args:
            directory_path: Percorso della directory contenente i documenti
            
        Returns:
            Lista di documenti caricati
        """
        documents = []
        
        if not directory_path.exists():
            logger.warning(f"Directory {directory_path} non trovata")
            return documents
        
        logger.info(f"Caricamento documenti da {directory_path}")
        
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in settings.SUPPORTED_EXTENSIONS:
                try:
                    doc_list = self._load_single_document(file_path)
                    documents.extend(doc_list)
                    logger.info(f"Caricato: {file_path.name} ({len(doc_list)} documenti)")
                except Exception as e:
                    logger.error(f"Errore nel caricamento di {file_path.name}: {e}")
        
        logger.info(f"Totale documenti caricati: {len(documents)}")
        return documents
    
    def _load_single_document(self, file_path: Path) -> List[Document]:
        """
        Carica un singolo documento
        
        Args:
            file_path: Percorso del file da caricare
            
        Returns:
            Lista di documenti (un file può generare più documenti)
        """
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.txt':
                # Gestione manuale per file di testo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return [Document(
                    text=content,
                    metadata={
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_type': 'text',
                        'source': file_path.stem
                    }
                )]
            
            elif extension in self.readers:
                # Usa i lettori di llama-index
                reader = self.readers[extension]
                documents = reader.load_data(file_path)
                
                # Aggiungi metadati
                for doc in documents:
                    doc.metadata.update({
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_type': extension[1:],  # rimuovi il punto
                        'source': file_path.stem
                    })
                
                return documents
            
            else:
                logger.warning(f"Tipo di file non supportato: {extension}")
                return []
                
        except Exception as e:
            raise RAGException(f"Errore nel caricamento del file {file_path.name}: {str(e)}")
    
    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """
        Crea un indice vettoriale dai documenti
        
        Args:
            documents: Lista di documenti da indicizzare
            
        Returns:
            Indice vettoriale creato
        """
        try:
            if not documents:
                raise RAGException("Nessun documento da indicizzare")
            
            logger.info(f"Creazione indice da {len(documents)} documenti")
            
            # Crea l'indice
            index = VectorStoreIndex.from_documents(
                documents,
                node_parser=self.node_parser,
                show_progress=True
            )
            
            logger.info("Indice creato con successo")
            return index
            
        except Exception as e:
            raise RAGException(f"Errore nella creazione dell'indice: {str(e)}")
    
    def save_index(self, index: VectorStoreIndex, save_path: Path) -> None:
        """
        Salva l'indice su disco
        
        Args:
            index: Indice da salvare
            save_path: Percorso dove salvare l'indice
        """
        try:
            save_path.mkdir(parents=True, exist_ok=True)
            index.storage_context.persist(persist_dir=str(save_path))
            logger.info(f"Indice salvato in {save_path}")
        except Exception as e:
            raise RAGException(f"Errore nel salvataggio dell'indice: {str(e)}")
    
    def load_index(self, index_path: Path) -> Optional[VectorStoreIndex]:
        """
        Carica un indice da disco
        
        Args:
            index_path: Percorso dell'indice salvato
            
        Returns:
            Indice caricato o None se non trovato
        """
        try:
            if not index_path.exists():
                logger.info(f"Indice non trovato in {index_path}")
                return None
            
            from llama_index.core import StorageContext, load_index_from_storage
            
            storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
            index = load_index_from_storage(storage_context)
            
            logger.info(f"Indice caricato da {index_path}")
            return index
            
        except Exception as e:
            logger.error(f"Errore nel caricamento dell'indice: {e}")
            return None
    
    def get_document_sources(self) -> List[str]:
        """
        Ottiene la lista delle fonti dei documenti caricati
        
        Returns:
            Lista dei nomi delle fonti
        """
        sources = set()
        for doc in self.documents:
            if 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
        return list(sources)
    
    def get_documents_by_source(self, source: str) -> List[Document]:
        """
        Filtra i documenti per fonte
        
        Args:
            source: Nome della fonte
            
        Returns:
            Lista di documenti della fonte specificata
        """
        return [
            doc for doc in self.documents 
            if doc.metadata.get('source') == source
        ]
    
    def update_documents(self, new_documents: List[Document]) -> None:
        """
        Aggiorna i documenti caricati
        
        Args:
            new_documents: Nuovi documenti da aggiungere
        """
        self.documents.extend(new_documents)
        logger.info(f"Aggiunti {len(new_documents)} nuovi documenti. Totale: {len(self.documents)}")
    
    def clear_documents(self) -> None:
        """Pulisce la lista dei documenti caricati"""
        self.documents.clear()
        logger.info("Lista documenti pulita")
