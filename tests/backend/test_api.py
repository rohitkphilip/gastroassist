import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest

# Import app module
from app.main import app

client = TestClient(app)

class TestAPI:
    @pytest.fixture
    def mock_pipeline(self):
        # Mock all pipeline components
        with patch("app.core.query_processor.QueryProcessor") as mock_qp, \
             patch("app.core.reasoning_agent.ReasoningAgent") as mock_ra, \
             patch("app.core.knowledge_router.KnowledgeRouter") as mock_kr, \
             patch("app.output.answer_generator.AnswerGenerator") as mock_ag, \
             patch("app.output.source_compiler.SourceCompiler") as mock_sc, \
             patch("app.output.quality_assurance.QualityAssurance") as mock_qa:
            
            # Configure mocks
            mock_qp_instance = MagicMock()
            mock_qp.return_value = mock_qp_instance
            mock_qp_instance.process.return_value = {"processed": "query"}
            
            mock_ra_instance = MagicMock()
            mock_ra.return_value = mock_ra_instance
            mock_ra_instance.analyze.return_value = {"info": "needs"}
            
            mock_kr_instance = MagicMock()
            mock_kr.return_value = mock_kr_instance
            mock_kr_instance.retrieve.return_value = {"knowledge": "results"}
            
            mock_ag_instance = MagicMock()
            mock_ag.return_value = mock_ag_instance
            mock_ag_instance.generate.return_value = "Generated answer"
            
            mock_sc_instance = MagicMock()
            mock_sc.return_value = mock_sc_instance
            mock_sc_instance.compile.return_value = [
                {"title": "Source 1", "url": "https://example.com/1", "snippet": "Info...", "confidence": 0.9}
            ]
            
            mock_qa_instance = MagicMock()
            mock_qa.return_value = mock_qa_instance
            mock_qa_instance.check.return_value = {
                "confidence_score": 0.85,
                "word_count": 150,
                "source_count": 1,
                "has_medical_sources": True
            }
            
            yield {
                "qp": mock_qp_instance,
                "ra": mock_ra_instance,
                "kr": mock_kr_instance,
                "ag": mock_ag_instance,
                "sc": mock_sc_instance,
                "qa": mock_qa_instance
            }
    
    def test_process_query_success(self, mock_pipeline):
        # Test successful query processing
        response = client.post(
            "/api/query",
            json={"text": "What are the symptoms of GERD?", "user_id": "test-user"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Verified answer"
        assert len(data["sources"]) == 1
        assert data["confidence_score"] == 0.85
        
        # Verify pipeline was called correctly
        mock_pipeline["qp"].process.assert_called_once_with("What are the symptoms of GERD?")
        mock_pipeline["ra"].analyze.assert_called_once_with({"processed": "query"})
        mock_pipeline["kr"].retrieve.assert_called_once_with({"info": "needs"})
        mock_pipeline["ag"].generate.assert_called_once_with({"knowledge": "results"}, {"processed": "query"})
        mock_pipeline["sc"].compile.assert_called_once_with({"knowledge": "results"})
        mock_pipeline["qa"].check.assert_called_once()
    
    def test_process_query_validation_error(self):
        # Test validation error (missing required field)
        response = client.post(
            "/api/query",
            json={"text": "What are the symptoms of GERD?"}  # Missing user_id
        )
        
        assert response.status_code == 422  # Validation error

