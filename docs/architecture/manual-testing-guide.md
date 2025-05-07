# Manual Testing Guide

## Overview

This document describes the process for manually testing the GastroAssist system, including how to use the pre-defined gastroenterology questions and interpret the results.

## Testing Prerequisites

Before running manual tests, ensure:

1. **Environment Setup**:
   - All dependencies installed: `pip install -r requirements.txt`
   - `.env` file configured with required API keys:
     ```
     TAVILY_API_KEY=your_tavily_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```
   - Internet access for external API calls

2. **Test Data**:
   - Pre-defined gastroenterology questions are available in `manual_testing/questions_manual.txt`
   - Expected answers are available in `manual_testing/Question_Answers_GastroAssist.xlsx`

## Testing Methods

### 1. Using the Test Pipeline Script

The `test_pipeline.py` script provides a direct way to test the enhanced pipeline with specific queries:

```bash
# Run with default test query
python scripts/test_pipeline.py

# Run with custom query
python scripts/test_pipeline.py "What is the most likely cause of chronic epigastric pain that improves with meals?"
```

This script:
- Initializes all pipeline components
- Processes the query through each pipeline stage
- Displays detailed results for each component
- Saves complete results to a JSON file in `app/output/pipeline_test_results.json`

### 2. Testing the API Endpoints

To test the complete system including API endpoints:

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Use tools like curl, Postman, or the FastAPI Swagger UI to send requests:
   ```bash
   curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"text": "What is the most likely cause of chronic epigastric pain that improves with meals?", "user_id": "test-user", "context": {}}'
   ```

3. Access the API documentation at `http://localhost:8000/docs` to interactively test endpoints

### 3. Running Multiple Test Questions

To test multiple questions automatically:

1. Use the pre-defined questions in `manual_testing/questions_manual.txt`
2. Run each question through the test script or API
3. Compare results with expected answers in the Excel file
4. Save test results to the `manual_testing/results` directory

## Result Analysis

When analyzing test results, evaluate:

1. **Search Quality**:
   - Are the search results relevant to the query?
   - Are medical domains prioritized in the results?
   - Are the top search results authoritative sources?

2. **Content Extraction**:
   - Was content successfully extracted from the URLs?
   - Is the extracted content relevant and complete?
   - Did the fallback mechanisms work if primary extraction failed?

3. **Summary Quality**:
   - Is the summary medically accurate?
   - Is the text concise and focused on the question?
   - Are sources properly cited?
   - Is medical terminology used appropriately?

4. **Overall Performance**:
   - Response time (should be under 15 seconds)
   - Error handling (all errors should be gracefully handled)
   - Confidence scores (should match expected quality)

## Documenting Test Results

Test results should be documented in standardized formats:

1. **CSV Reports**:
   - Question ID
   - Question Text
   - Response
   - Confidence Score
   - Processing Time
   - Pass/Fail Assessment

2. **JSON Results**:
   - Complete pipeline results
   - All intermediary outputs
   - Error messages (if any)

3. **TXT Reports**:
   - Human-readable summary of test results
   - Overall pass rate
   - Notes on specific test cases

## Troubleshooting Common Issues

1. **API Authentication Errors**:
   - Verify API keys in the `.env` file
   - Check for API rate limits or quotas

2. **Content Extraction Issues**:
   - Check URL accessibility
   - Verify Tavily API status
   - Test alternative extraction methods

3. **Summarization Problems**:
   - Verify OpenAI API status
   - Check for context length issues
   - Review prompt formatting

4. **Performance Issues**:
   - Monitor API response times
   - Check for memory usage in long-running tests
   - Consider running tests in batches

## Integration with CI/CD

Future improvements will integrate manual testing with CI/CD:

1. Automated test runs with each commit
2. Regression testing against baseline results
3. Performance benchmarking across versions
4. Integration with monitoring and alerting
