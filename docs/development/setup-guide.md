# Development Setup Guide

This guide will help you set up your development environment for GastroAssist AI.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher (for frontend development)
- Git

## Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/gastroassist-ai.git
   cd gastroassist-ai
   ```

2. **Create a virtual environment**

   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment variables**

   Create a `.env` file in the project root:

   ```
   TAVILY_API_KEY=your_tavily_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Verify the directory structure**

   Ensure all required files exist:

   ```bash
   # Create any missing __init__.py files
   mkdir -p app/core app/knowledge/search_engines app/output
   touch app/__init__.py
   touch app/core/__init__.py
   touch app/knowledge/__init__.py
   touch app/knowledge/search_engines/__init__.py
   touch app/output/__init__.py
   ```

6. **Run the backend server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000

## Frontend Setup

1. **Navigate to the frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start the development server**

   ```bash
   npm run dev
   ```

   The frontend will be available at http://localhost:3000

## Running Tests

1. **Run backend tests**

   ```bash
   # Make sure you're in the project root
   cd ..
   pytest
   ```

2. **Run frontend tests**

   ```bash
   cd frontend
   npm test
   ```

## Common Issues and Solutions

### Module Import Errors

If you encounter module import errors like `No module named 'app.core.query_processor'` or similar:

1. Make sure your virtual environment is activated
2. Verify that all required files exist in the correct directory structure
3. Check that all directories have `__init__.py` files
4. Make sure you're running commands from the project root
5. If running tests, make sure `pytest.ini` exists with the correct configuration

### API Key Issues

If you encounter API key errors:

1. Check that your `.env` file exists and contains the correct keys
2. Make sure there are no spaces around the `=` sign
3. Verify that your API keys are valid and have sufficient credits

### Port Already in Use

If you encounter "Port already in use" errors:

1. Change the port for the backend:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

2. Change the port for the frontend:
   ```bash
   # In package.json, modify the dev script to use a different port
   # Or use the following command
   npm run dev -- -p 3001
   ```

## Next Steps

After setting up your development environment:

1. Read the [Architecture Documentation](../architecture/system-overview.md)
2. Review the [API Documentation](../api/endpoints.md)
3. Check out the [Contributing Guidelines](../development/contributing.md)
