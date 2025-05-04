import pytest
from unittest.mock import MagicMock, patch
from app.core.knowledge_router import KnowledgeRouter

class TestKnowledgeRouter:
    @pytest.fixture
    def mock_kb(self):
        mock = MagicMock()
        mock.query.return_value = {"results": ["kb_result_1", "kb_result_2"]}
        return mock
    
    @pytest.fixture
    def mock_dynamic_search(self):
        mock = MagicMock()
        mock.search.return_value = {
            "medical": ["medical_result_1"],
            "general": ["general_result_1", "general_result_2"]
        }
        return mock
    
    @pytest.fixture
    def router(self, mock_kb, mock_dynamic_search):
        with patch("app.knowledge.kb_connector.GastroKnowledgeBase", return_value=mock_kb):
            with patch("app.knowledge.dynamic_search.DynamicSearch", return_value=mock_dynamic_search):
                return KnowledgeRouter()
    
    def test_retrieve_kb_only(self, router, mock_kb, mock_dynamic_search):
        # Test when only KB is required
        info_needs = {
            "query": "What are the symptoms of GERD?",
            "requires_kb": True,
            "requires_dynamic_search": False
        }
        
        results = router.retrieve(info_needs)
        
        mock_kb.query.assert_called_once_with(info_needs["query"], filters={})
        mock_dynamic_search.search.assert_not_called()
        assert "kb_results" in results
        assert "search_results" not in results
    
    def test_retrieve_dynamic_search_only(self, router, mock_kb, mock_dynamic_search):
        # Test when only dynamic search is required
        info_needs = {
            "query": "Latest research on IBD treatments",
            "requires_kb": False,
            "requires_dynamic_search": True,
            "search_type": "medical"
        }
        
        results = router.retrieve(info_needs)
        
        mock_kb.query.assert_not_called()
        mock_dynamic_search.search.assert_called_once_with(
            info_needs["query"], 
            search_type="medical"
        )
        assert "kb_results" not in results
        assert "search_results" in results
    
    def test_retrieve_combined(self, router, mock_kb, mock_dynamic_search):
        # Test when both KB and dynamic search are required
        info_needs = {
            "query": "Crohn's disease new treatments",
            "requires_kb": True,
            "requires_dynamic_search": True,
            "search_type": "combined",
            "kb_filters": {"category": "treatment"}
        }
        
        results = router.retrieve(info_needs)
        
        mock_kb.query.assert_called_once_with(
            info_needs["query"], 
            filters={"category": "treatment"}
        )
        mock_dynamic_search.search.assert_called_once_with(
            info_needs["query"], 
            search_type="combined"
        )
        assert "kb_results" in results
        assert "search_results" in results