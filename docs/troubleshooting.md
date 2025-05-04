# Troubleshooting Guide

This guide helps you solve common issues you might encounter when setting up or running GastroAssist AI.

## Backend Issues

### Installation Problems

**Problem**: `pip install` fails with dependency errors.

**Solution**:
1. Make sure you're using Python 3.11+
   ```bash
   python --version
   ```
2. Update pip
   ```bash
   pip install --upgrade pip
   ```
3. Try installing dependencies one by one to identify the problematic package

**Problem**: Virtual environment activation doesn't work.

**Solution**:
- On Windows, make sure you're running `venv\Scripts\activate`
- On macOS/Linux, use `source venv/bin/activate`
- If using VS Code, select the correct Python interpreter (View > Command Palette > Python: Select Interpreter)

### Testing Issues

**Problem**: `ModuleNotFoundError: No module named 'app'` when running tests.

**Solution**:
1. Create a `pytest.ini` file in the project root:
   ```ini
   [pytest]
   pythonpath = .
   testpaths = tests
   ```

2. Alternatively, set the PYTHONPATH environment variable:
   ```bash
   # On Windows
   set PYTHONPATH=.
   
   # On macOS/Linux
   export PYTHONPATH=.
   ```

3. Or install the package in development mode:
   ```bash
   pip install -e .
   ```

**Problem**: `ModuleNotFoundError: No module named 'app.knowledge.kb_connector'` or similar.

**Solution**:
1. Make sure all required module files exist in the correct directory structure:
   ```
   app/
   ├── __init__.py
   ├── core/
   │   ├── __init__.py
   │   ├── query_processor.py
   │   ├── reasoning_agent.py
   │   └── knowledge_router.py
   ├── knowledge/
   │   ├── __init__.py
   │   ├── kb_connector.py
   │   ├── dynamic_search.py
   │   └── search_engines/
   │       ├── __init__.py
   │       ├── tavily_search.py
   │       └── duckduckgo_search.py
   └── output/
       ├── __init__.py
       ├── answer_generator.py
       ├── source_compiler.py
       └── quality_assurance.py
   ```

2. Create any missing `__init__.py` files in each directory:
   ```bash
   # Create __init__.py files in
   touch app/__init__.py
   touch app/core/__init__.py
   touch app/knowledge/__init__.py
   touch app/knowledge/search_engines/__init__.py
   touch app/output/__init__.py
   ```

3. If you're still having issues, check for typos in import statements

### Server Startup Issues

**Problem**: `uvicorn` command not found.

**Solution**:
1. Make sure your virtual environment is activated
2. Install uvicorn directly
   ```bash
   pip install uvicorn
   ```

**Problem**: Server starts but shows API key errors.

**Solution**:
1. Check that your `.env` file exists in the project root
2. Verify API keys are correctly formatted without quotes
3. Make sure there are no spaces around the `=` sign

**Problem**: Port already in use.

**Solution**:
1. Change the port
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
2. Find and stop the process using the port
   - Windows: `netstat -ano | findstr :8000`
   - macOS/Linux: `lsof -i :8000`

## Frontend Issues

**Problem**: `npm install` fails with dependency errors.

**Solution**:
1. Make sure you're using Node.js 18+
   ```bash
   node --version
   ```
2. Clear npm cache
   ```bash
   npm cache clean --force
   ```
3. Delete `node_modules` folder and `package-lock.json`, then try again
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

**Problem**: Frontend can't connect to backend API.

**Solution**:
1. Make sure backend server is running
2. Check that `.env.local` has the correct API URL
3. Verify there are no CORS issues (check browser console)
4. Try accessing the API directly in the browser (http://localhost:8000/docs)

**Problem**: Page shows blank screen or React errors.

**Solution**:
1. Check browser console for errors
2. Make sure all required environment variables are set
3. Try clearing browser cache or using incognito mode

## Database Issues

**Problem**: Database connection errors.

**Solution**:
1. Check that your database URL is correct in `.env`
2. For SQLite, make sure the directory is writable
3. For PostgreSQL/MySQL, verify the database exists and credentials are correct

**Problem**: Migration errors.

**Solution**:
1. Delete the existing database file (if using SQLite)
2. Run the initialization script again
   ```bash
   python -m app.db.init_db
   ```

## API Integration Issues

**Problem**: OpenAI API errors.

**Solution**:
1. Verify your API key is valid and has sufficient credits
2. Check that you're not exceeding rate limits
3. Make sure you're using a supported model

**Problem**: Tavily Search API errors.

**Solution**:
1. Verify your API key is valid
2. Check the search query format
3. Make sure you're not exceeding rate limits

## Still Having Issues?

If you're still experiencing problems:

1. Search our GitHub issues to see if someone else has encountered the same problem
2. Check the logs for more detailed error messages
3. Join our developer Discord channel for real-time help
4. Create a new GitHub issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Your environment details (OS, Python/Node versions)


