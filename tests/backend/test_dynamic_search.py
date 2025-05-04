import pytest
from unittest.mock import MagicMock, patch
from app.knowledge.dynamic_search import DynamicSearch

class TestDynamicSearch:
    @pytest.fixture
    def mock_tavily(self):
        mock = MagicMock()
        mock.search.return_value = [
            {"title": "Medical Study 1", "url": "https://example.com/study1", "snippet": "Study details..."},
            {"title": "Medical Study 2", "url": "https://example.com/study2", "snippet": "More details..."}
        ]
        return mock
    
    @pytest.fixture
    def mock_duckduckgo(self):
        mock = MagicMock()
        mock.search.return_value = [
            {"title": "General Info 1", "url": "https://example.com/info1", "snippet": "General info..."},
            {"title": "General Info 2", "url": "https://example.com/info2", "snippet": "More info..."}
        ]
        return mock
    
    @pytest.fixture
    def dynamic_search(self, mock_tavily, mock_duckduckgo):
        with patch("app.knowledge.search_engines.tavily_search.TavilySearch", return_value=mock_tavily):
            with patch("app.knowledge.search_engines.duckduckgo_search.DuckDuckGoSearch", return_value=mock_duckduckgo):
                return DynamicSearch()
    
    def test_search_medical_only(self, dynamic_search, mock_tavily, mock_duckduckgo):
        # Test medical-only search
        query = "Latest GERD treatment guidelines"
        results = dynamic_search.search(query, search_type="medical")
        
        mock_tavily.search.assert_called_once_with(
            query=query,
            search_depth="comprehensive",
            filter_medical=True
        )
        mock_duckduckgo.search.assert_not_called()
        
        assert "medical" in results
        assert "general" not in results
    
    def test_search_general_only(self, dynamic_search, mock_tavily, mock_duckduckgo):
        # Test general-only search
        query = "Patient diet recommendations"
        results = dynamic_search.search(query, search_type="general")
        
        mock_tavily.search.assert_not_called()
        mock_duckduckgo.search.assert_called_once_with(
            query=query,
            max_results=10
        )
        
        assert "medical" not in results
        assert "general" in results
    
    def test_search_combined(self, dynamic_search, mock_tavily, mock_duckduckgo):
        # Test combined search
        query = "Ulcerative colitis treatments"
        results = dynamic_search.search(query, search_type="combined")
        
        mock_tavily.search.assert_called_once_with(
            query=query,
            search_depth="comprehensive",
            filter_medical=True
        )
        mock_duckduckgo.search.assert_called_once_with(
            query=query,
            max_results=10
        )
        
        assert "medical" in results
        assert "general" in results