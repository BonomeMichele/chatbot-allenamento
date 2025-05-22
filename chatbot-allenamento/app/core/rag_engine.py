"""
Motore RAG (Retrieval-Augmented Generation)
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from app.config import settings
from app.core.embeddings import EmbeddingManager
from app.core.error_handler import RAGException

logger = logging.getLogger(__name__)

class RAGEngine:
    """Motore RAG per il recupero e la generazione di informazioni"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Inizializza il motore RAG"""
        async with self._initialization_lock:
            if self._initialized:
                return
            
            try:
                logger.info("🔄 Inizializzazione motore RAG...")
                
                # Prova a caricare un indice esistente
                index_path = settings.VECTOR_STORE_PATH
                self.index = self.embedding_manager.load_index(index_path)
                
                if self.index is None:
                    # Crea un nuovo indice dai documenti
                    await self._create_new_index()
                else:
                    logger.info("✅ Indice esistente caricato")
                
                # Configura il query engine
                self._setup_query_engine()
                
                self._initialized = True
                logger.info("🎉 Motore RAG inizializzato con successo")
                
            except Exception as e:
                logger.error(f"❌ Errore nell'inizializzazione del motore RAG: {e}")
                raise RAGException(f"Errore nell'inizializzazione del motore RAG: {str(e)}")
    
    async def _create_new_index(self) -> None:
        """Crea un nuovo indice dai documenti"""
        logger.info("📚 Caricamento documenti da directory...")
        
        # Carica i documenti dalla directory
        documents = self.embedding_manager.load_documents_from_directory(
            settings.DOCUMENTS_PATH
        )
        
        if not documents:
            logger.warning("⚠️ Nessun documento trovato nella directory")
            # Crea un indice vuoto per evitare errori
            from llama_index.core import Document
            dummy_doc = Document(text="Documento placeholder per inizializzazione RAG")
            documents = [dummy_doc]
        
        # Aggiorna i documenti nel manager
        self.embedding_manager.update_documents(documents)
        
        # Crea l'indice
        logger.info("🔍 Creazione indice vettoriale...")
        self.index = self.embedding_manager.create_index(documents)
        
        # Salva l'indice
        logger.info("💾 Salvataggio indice...")
        self.embedding_manager.save_index(self.index, settings.VECTOR_STORE_PATH)
    
    def _setup_query_engine(self) -> None:
        """Configura il query engine"""
        if not self.index:
            raise RAGException("Indice non disponibile per la configurazione del query engine")
        
        # Configura il retriever
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=settings.TOP_K_DOCUMENTS
        )
        
        # Configura il postprocessor per filtrare per similarità
        postprocessor = SimilarityPostprocessor(
            similarity_cutoff=settings.SIMILARITY_THRESHOLD
        )
        
        # Crea il query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=[postprocessor]
        )
        
        logger.info("🔧 Query engine configurato")
    
    async def retrieve_context(self, query: str) -> Tuple[str, List[str]]:
        """
        Recupera il contesto rilevante per una query
        
        Args:
            query: Query di ricerca
            
        Returns:
            Tupla contenente (contesto_combinato, lista_fonti)
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.query_engine:
            raise RAGException("Query engine non configurato")
        
        try:
            logger.info(f"🔍 Ricerca contesto per: {query[:100]}...")
            
            # Esegui la query
            response = self.query_engine.query(query)
            
            # Estrai i nodi sorgente
            source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else []
            
            # Combina il testo dei nodi rilevanti
            context_parts = []
            sources = set()
            
            for node in source_nodes:
                if hasattr(node, 'node'):
                    text = node.node.text
                    metadata = node.node.metadata
                    
                    context_parts.append(text)
                    
                    # Aggiungi la fonte
                    if 'source' in metadata:
                        sources.add(metadata['source'])
                    elif 'filename' in metadata:
                        sources.add(metadata['filename'])
            
            # Combina il contesto
            combined_context = "\n\n".join(context_parts)
            source_list = list(sources)
            
            logger.info(f"✅ Recuperati {len(context_parts)} frammenti da {len(source_list)} fonti")
            
            return combined_context, source_list
            
        except Exception as e:
            logger.error(f"❌ Errore nel recupero del contesto: {e}")
            raise RAGException(f"Errore nel recupero del contesto: {str(e)}")
    
    async def search_documents(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Cerca documenti rilevanti
        
        Args:
            query: Query di ricerca
            top_k: Numero massimo di risultati
            
        Returns:
            Lista di documenti rilevanti con metadata
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.index:
            raise RAGException("Indice non disponibile")
        
        try:
            k = top_k or settings.TOP_K_DOCUMENTS
            retriever = VectorIndexRetriever(index=self.index, similarity_top_k=k)
            
            # Esegui la ricerca
            nodes = retriever.retrieve(query)
            
            results = []
            for node in nodes:
                if hasattr(node, 'node'):
                    results.append({
                        'text': node.node.text,
                        'metadata': node.node.metadata,
                        'score': getattr(node, 'score', 0.0)
                    })
            
            logger.info(f"🔍 Trovati {len(results)} documenti per la query")
            return results
            
        except Exception as e:
            logger.error(f"❌ Errore nella ricerca documenti: {e}")
            raise RAGException(f"Errore nella ricerca documenti: {str(e)}")
    
    async def add_documents(self, file_paths: List[Path]) -> None:
        """
        Aggiunge nuovi documenti all'indice
        
        Args:
            file_paths: Lista dei percorsi dei file da aggiungere
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"📥 Aggiunta di {len(file_paths)} nuovi documenti...")
            
            # Carica i nuovi documenti
            new_documents = []
            for file_path in file_paths:
                if file_path.exists():
                    docs = self.embedding_manager._load_single_document(file_path)
                    new_documents.extend(docs)
            
            if not new_documents:
                logger.warning("⚠️ Nessun documento valido da aggiungere")
                return
            
            # Aggiorna l'indice
            for doc in new_documents:
                self.index.insert(doc)
            
            # Aggiorna il manager
            self.embedding_manager.update_documents(new_documents)
            
            # Salva l'indice aggiornato
            self.embedding_manager.save_index(self.index, settings.VECTOR_STORE_PATH)
            
            logger.info(f"✅ Aggiunti {len(new_documents)} documenti all'indice")
            
        except Exception as e:
            logger.error(f"❌ Errore nell'aggiunta documenti: {e}")
            raise RAGException(f"Errore nell'aggiunta documenti: {str(e)}")
    
    async def refresh_index(self) -> None:
        """Ricostruisce l'indice da zero"""
        try:
            logger.info("🔄 Ricostruzione dell'indice...")
            
            # Pulisci l'indice esistente
            self.index = None
            self.query_engine = None
            self.embedding_manager.clear_documents()
            
            # Ricrea l'indice
            await self._create_new_index()
            self._setup_query_engine()
            
            logger.info("✅ Indice ricostruito con successo")
            
        except Exception as e:
            logger.error(f"❌ Errore nella ricostruzione dell'indice: {e}")
            raise RAGException(f"Errore nella ricostruzione dell'indice: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sull'indice
        
        Returns:
            Dizionario con le statistiche
        """
        stats = {
            'initialized': self._initialized,
            'index_available': self.index is not None,
            'query_engine_available': self.query_engine is not None,
            'total_documents': len(self.embedding_manager.documents),
            'available_sources': self.embedding_manager.get_document_sources()
        }
        
        return stats
    
    def is_initialized(self) -> bool:
        """Verifica se il motore RAG è inizializzato"""
        return self._initialized
    
    async def get_sources_summary(self) -> List[Dict[str, Any]]:
        """
        Ottiene un riassunto delle fonti disponibili
        
        Returns:
            Lista con informazioni sulle fonti
        """
        sources_info = []
        
        for source in self.embedding_manager.get_document_sources():
            docs = self.embedding_manager.get_documents_by_source(source)
            
            total_chars = sum(len(doc.text) for doc in docs)
            
            sources_info.append({
                'source': source,
                'document_count': len(docs),
                'total_characters': total_chars,
                'file_types': list(set(doc.metadata.get('file_type', 'unknown') for doc in docs))
            })
        
        return sources_info
