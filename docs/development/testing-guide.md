# Testing Guide

This document outlines the testing approach for the GastroAssist AI system, including test types, tools, and best practices.

## Testing Philosophy

GastroAssist AI follows a comprehensive testing strategy to ensure high-quality, reliable software:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete user flows
4. **Performance Tests**: Ensure system meets performance requirements

## Backend Testing

### Setup

Backend tests use pytest as the test runner:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app
```

### Fixing Module Import Errors

If you encounter `ModuleNotFoundError: No module named 'app'` when running tests, there are several ways to fix it:

1. **Using pytest.ini (Recommended)**
   
   Create a `pytest.ini` file in the project root with:
   ```ini
   [pytest]
   pythonpath = .
   testpaths = tests
   ```

2. **Using conftest.py**
   
   Create or update `tests/conftest.py` with:
   ```python
   import os
   import sys
   
   # Add the project root directory to Python path
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   ```

3. **Using PYTHONPATH environment variable**
   
   Set the PYTHONPATH before running tests:
   ```bash
   # On Windows
   set PYTHONPATH=.
   
   # On macOS/Linux
   export PYTHONPATH=.
   
   # Then run tests
   pytest
   ```

4. **Install the package in development mode**
   
   ```bash
   pip install -e .
   ```

### Test Structure

Backend tests are organized by component:

- `tests/backend/core/`: Tests for core system components
- `tests/backend/knowledge/`: Tests for knowledge sources
- `tests/backend/output/`: Tests for response generation
- `tests/backend/api/`: API endpoint tests

### Mocking

We use pytest's monkeypatch and unittest.mock for mocking dependencies:

```python
# Example of mocking an external API
def test_tavily_search(monkeypatch):
    # Mock the requests.post function
    def mock_post(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [...]}
        mock_response.status_code = 200
        return mock_response
    
    monkeypatch.setattr("requests.post", mock_post)
    
    # Test the search function
    tavily = TavilySearch()
    results = tavily.search("test query")
    assert len(results) > 0
```

## Frontend Testing

### Setup

Frontend tests use Jest and React Testing Library:

```bash
# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run all tests
npm test

# Run with coverage
npm test -- --coverage
```

### Test Structure

Frontend tests are organized by feature:

- `tests/frontend/components/`: UI component tests
- `tests/frontend/store/`: Redux store tests
- `tests/frontend/pages/`: Page component tests
- `tests/frontend/e2e/`: End-to-end tests

### Component Testing

We test components for:
- Correct rendering
- User interactions
- State changes
- Props handling

```tsx
// Example component test
test('shows loading state', () => {
  render(<ResponseDisplay loading={true} />);
  expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
});
```

## End-to-End Testing

End-to-end tests use Cypress to test complete user flows:

```bash
# Install Cypress
npm install --save-dev cypress

# Open Cypress test runner
npx cypress open
```

Example E2E test:

```javascript
describe('Query Flow', () => {
  it('should submit a query and display results', () => {
    cy.visit('/');
    cy
```

### Manual Testing Workflow

The complete manual testing workflow includes:

1. **Prepare**: Create question files in the `manual_testing` directory
2. **Verify**: Run `python scripts/verify_manual_testing.py` to check setup
3. **Test**: Execute `python scripts/run_manual_tests.py` to run tests
4. **Report**: Generate reports with `python scripts/generate_test_report.py`
5. **Extract**: Extract detailed summaries with `python scripts/extract_test_summaries.py`
6. **Analyze**: Review reports and summaries to evaluate system performance

This workflow allows for systematic evaluation of the system's response quality across different question types and domains.
