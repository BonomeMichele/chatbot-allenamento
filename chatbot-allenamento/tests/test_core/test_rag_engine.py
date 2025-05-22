"""
Test per RAGEngine
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from app.core.rag_engine import RAGEngine
from app.core.error_handler import RAGException

class TestRAGEngine:
    """Test per il motore RAG"""
    
    @pytest.fixture
    def rag_engine(self):
        """Fixture per RAGEngine"""
        return RAGEngine()
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, rag_engine, temp_dir):
        """Test inizializzazione con successo"""
        with patch('app.config.settings') as mock_settings:
            mock_settings.VECTOR_STORE_PATH = temp_dir / "indexes"
            mock_settings.DOCUMENTS_PATH = temp_dir / "documents"
            
            # Mock embedding manager
            rag_engine.embedding_manager.load_index = Mock(return_value=None)
            rag_engine.embedding_manager.load_documents_from_directory = Mock(return_value=[])
            rag_engine.embedding_manager.create_index = Mock(return_value=Mock())
            rag_engine.embedding_manager.save_index = Mock()
            
            await rag_engine.initialize()
            
            assert rag_engine._initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_with_existing_index(self, rag_engine):
        """Test inizializzazione con indice esistente"""
        mock_index = Mock()
        rag_engine.embedding_manager.load_index = Mock(return_value=mock_index)
        
        await rag_engine.initialize()
        
        assert rag_engine.index == mock_index
        assert rag_engine._initialized is True
    
    @pytest.mark.asyncio
    async def test_retrieve_context_success(self, rag_engine):
        """Test recupero contesto con successo"""
        # Setup
        rag_engine._initialized = True
        mock_response = Mock()
        mock_response.source_nodes = [
            Mock(node=Mock(text="Testo 1", metadata={"source": "doc1.pdf"})),
            Mock(node=Mock(text="Testo 2", metadata={"source": "doc2.pdf"}))
        ]
        
        mock_query_engine = Mock()
        mock_query_engine.query = Mock(return_value=mock_response)
        rag_engine.query_engine = mock_query_engine
        
        # Test
        context, sources = await rag_engine.retrieve_context("test query")
        
        assert "Testo 1" in context
        assert "Testo 2" in context
        assert "doc1.pdf" in sources
        assert "doc2.pdf" in sources
    
    @pytest.mark.asyncio
    async def test_retrieve_context_not_initialized(self, rag_engine):
        """Test recupero contesto senza inizializzazione"""
        rag_engine._initialized = False
        rag_engine.initialize = AsyncMock()
        rag_engine.query_engine = Mock()
        
        mock_response = Mock()
        mock_response.source_nodes = []
        rag_engine.query_engine.query = Mock(return_value=mock_response)
        
        await rag_engine.retrieve_context("test")
        
        rag_engine.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_documents_success(self, rag_engine):
        """Test ricerca documenti"""
        rag_engine._initialized = True
        rag_engine.index = Mock()
        
        mock_nodes = [
            Mock(node=Mock(
                text="Documento di test",
                metadata={"source": "test.pdf"}
            ), score=0.9)
        ]
        
        with patch('app.core.rag_engine.VectorIndexRetriever') as mock_retriever_class:
            mock_retriever = Mock()
            mock_retriever.retrieve = Mock(return_value=mock_nodes)
            mock_retriever_class.return_value = mock_retriever
            
            results = await rag_engine.search_documents("query test")
            
            assert len(results) == 1
            assert results[0]["text"] == "Documento di test"
            assert results[0]["metadata"]["source"] == "test.pdf"
            assert results[0]["score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_add_documents_success(self, rag_engine, temp_dir):
        """Test aggiunta documenti"""
        rag_engine._initialized = True
        rag_engine.index = Mock()
        
        # Crea file di test
        test_file = temp_dir / "test.txt"
        test_file.write_text("Contenuto di test")
        
        rag_engine.embedding_manager._load_single_document = Mock(
            return_value=[Mock(text="Contenuto di test")]
        )
        rag_engine.embedding_manager.update_documents = Mock()
        rag_engine.embedding_manager.save_index = Mock()
        
        await rag_engine.add_documents([test_file])
        
        rag_engine.index.insert.assert_called()
        rag_engine.embedding_manager.update_documents.assert_called()
        rag_engine.embedding_manager.save_index.assert_called()
    
    @pytest.mark.asyncio
    async def test_refresh_index_success(self, rag_engine):
        """Test ricostruzione indice"""
        rag_engine._initialized = True
        rag_engine.index = Mock()
        rag_engine.query_engine = Mock()
        rag_engine.embedding_manager.clear_documents = Mock()
        rag_engine._create_new_index = AsyncMock()
        rag_engine._setup_query_engine = Mock()
        
        await rag_engine.refresh_index()
        
        assert rag_engine.index is None
        assert rag_engine.query_engine is None
        rag_engine.embedding_manager.clear_documents.assert_called_once()
        rag_engine._create_new_index.assert_called_once()
        rag_engine._setup_query_engine.assert_called_once()
    
    def test_get_index_stats(self, rag_engine):
        """Test statistiche indice"""
        rag_engine._initialized = True
        rag_engine.index = Mock()
        rag_engine.query_engine = Mock()
        rag_engine.embedding_manager.documents = [Mock(), Mock()]
        rag_engine.embedding_manager.get_document_sources = Mock(return_value=["doc1", "doc2"])
        
        stats = rag_engine.get_index_stats()
        
        assert stats["initialized"] is True
        assert stats["index_available"] is True
        assert stats["query_engine_available"] is True
        assert stats["total_documents"] == 2
        assert stats["available_sources"] == ["doc1", "doc2"]
    
    def test_is_initialized(self, rag_engine):
        """Test verifica inizializzazione"""
        assert rag_engine.is_initialized() is False
        
        rag_engine._initialized = True
        assert rag_engine.is_initialized() is True
    
    @pytest.mark.asyncio
    async def test_get_sources_summary(self, rag_engine):
        """Test riassunto fonti"""
        mock_docs = [
            Mock(text="a" * 100, metadata={"file_type": "pdf"}),
            Mock(text="b" * 200, metadata={"file_type": "pdf"})
        ]
        
        rag_engine.embedding_manager.get_document_sources = Mock(return_value=["test_source"])
        rag_engine.embedding_manager.get_documents_by_source = Mock(return_value=mock_docs)
        
        summary = await rag_engine.get_sources_summary()
        
        assert len(summary) == 1
        assert summary[0]["source"] == "test_source"
        assert summary[0]["document_count"] == 2
        assert summary[0]["total_characters"] == 300
        assert summary[0]["file_types"] == ["pdf"]
    
    @pytest.mark.asyncio
    async def test_error_handling_in_retrieve_context(self, rag_engine):
        """Test gestione errori nel recupero contesto"""
        rag_engine._initialized = True
        rag_engine.query_engine = Mock()
        rag_engine.query_engine.query = Mock(side_effect=Exception("Test error"))
        
        with pytest.raises(RAGException) as exc_info:
            await rag_engine.retrieve_context("test query")
        
        assert "Errore nel recupero del contesto" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_add_documents(self, rag_engine, temp_dir):
        """Test gestione errori nell'aggiunta documenti"""
        rag_engine._initialized = True
        rag_engine.index = Mock()
        rag_engine.index.insert = Mock(side_effect=Exception("Insert error"))
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        rag_engine.embedding_manager._load_single_document = Mock(
            return_value=[Mock(text="Test content")]
        )
        
        with pytest.raises(RAGException) as exc_info:
            await rag_engine.add_documents([test_file])
        
        assert "Errore nell'aggiunta documenti" in str(exc_info.value)
