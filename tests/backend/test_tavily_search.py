import pytest
from unittest.mock import MagicMock, patch
import requests
import os
from app.knowledge.search_engines.tavily_search import TavilySearch

class TestTavilySearch:
    @pytest.fixture
    def mock_env(self, monkeypatch):
        monkeypatch.setenv("TAVILY_API_KEY", "test-api-key")
    
    @pytest.fixture
    def tavily_search(self, mock_env):
        return TavilySearch()
    
    def test_init_missing_api_key(self, monkeypatch):
        # Test initialization with missing API key
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        with pytest.raises(ValueError, match="TAVILY_API_KEY environment variable is not set"):
            TavilySearch()
    
    def test_search_success(self, tavily_search):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "content": "This is test content 1",
                    "score": 0.95
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "content": "This is test content 2",
                    "score": 0.85
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.post", return_value=mock_response) as mock_post:
            results = tavily_search.search("test query", search_depth="basic", filter_medical=False)
            
            # Verify API call
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            
            # Check URL
            assert args[0] == "https://api.tavily.com/search"
            
            # Check headers
            assert kwargs["headers"]["X-API-Key"] == "test-api-key"
            assert kwargs["headers"]["Content-Type"] == "application/json"
            
            # Check payload
            assert kwargs["json"]["query"] == "test query"
            assert kwargs["json"]["search_depth"] == "basic"
            assert "topic" not in kwargs["json"]
            
            # Check results
            assert len(results) == 2
            assert results[0]["title"] == "Test Result 1"
            assert results[0]["url"] == "https://example.com/1"
            assert results[0]["snippet"] == "This is test content 1"
            assert results[0]["score"] == 0.95
    
    def test_search_with_medical_filter(self, tavily_search):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.post", return_value=mock_response) as mock_post:
            tavily_search.search("medical query", search_depth="comprehensive", filter_medical=True)
            
            # Verify API call
            args, kwargs = mock_post.call_args
            
            # Check medical-specific parameters
            assert kwargs["json"]["topic"] == "medical"
            assert kwargs["json"]["search_depth"] == "comprehensive"
            assert "search_filters" in kwargs["json"]
            assert "include_domains" in kwargs["json"]["search_filters"]
            assert "pubmed.ncbi.nlm.nih.gov" in kwargs["json"]["search_filters"]["include_domains"]
    
    def test_search_request_exception(self, tavily_search):
        # Test handling of request exception
        with patch("requests.post", side_effect=requests.exceptions.RequestException("Test error")):
            results = tavily_search.search("test query")
            
            # Should return empty results on error
            assert results == []
    
    def test_search_json_decode_error(self, tavily_search):
        # Test handling of JSON decode error
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        
        with patch("requests.post", return_value=mock_response):
            results = tavily_search.search("test query")
            
            # Should return empty results on error
            assert results == []