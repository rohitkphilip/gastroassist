# Environment Variables Guide

This document explains all environment variables used by GastroAssist and how to configure them properly.

## Overview

GastroAssist uses environment variables to manage configuration settings without hardcoding sensitive information in the codebase. These variables are stored in a `.env` file in the project root.

## Required Variables

### API Keys

```
# OpenAI API key for LLM summarization
OPENAI_API_KEY=your_openai_api_key

# Tavily API key for search and content extraction
TAVILY_API_KEY=your_tavily_api_key
```

You can obtain these API keys from:
- OpenAI API Key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Tavily API Key: [https://tavily.com/dashboard](https://tavily.com/dashboard)

### Database Configuration

```
# SQLite (development)
DATABASE_URL=sqlite:///./gastroassist.db

# PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/gastroassist
```

### Application Settings

```
# Debug mode (enables detailed error messages)
DEBUG=True

# Host and port for the API server
HOST=0.0.0.0
PORT=8000
```

## Optional Variables

### LLM Configuration

```
# LLM service to use for evaluation (openai or groq)
LLM_SERVICE=openai

# OpenAI model (if using OpenAI)
OPENAI_MODEL=gpt-3.5-turbo

# Groq API key and model (if using Groq for evaluation)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-70b-8192
```

### Search Configuration

```
# Maximum number of search results to retrieve
MAX_SEARCH_RESULTS=5

# Maximum number of sources to extract content from
MAX_EXTRACT_SOURCES=3

# Maximum tokens for summarization
MAX_SUMMARY_TOKENS=500
```

### Performance Settings

```
# Enable caching of search results
ENABLE_CACHE=True

# Cache expiration time in seconds
CACHE_EXPIRATION=3600
```

### Logging Configuration

```
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path
LOG_FILE=logs/gastroassist.log
```

## Setting Up Environment Variables

### Local Development

1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Add the required variables to the file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   DATABASE_URL=sqlite:///./gastroassist.db
   DEBUG=True
   ```

3. Load variables in Python code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Production Deployment

For production environments, set environment variables securely using your hosting platform's methods:

#### Docker

In your `docker-compose.yml`:
```yaml
services:
  app:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - DEBUG=False
```

#### Heroku

```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key
heroku config:set TAVILY_API_KEY=your_tavily_api_key
heroku config:set DATABASE_URL=your_database_url
```

#### AWS Elastic Beanstalk

Create a `.ebextensions/environment.config` file:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    OPENAI_API_KEY: your_openai_api_key
    TAVILY_API_KEY: your_tavily_api_key
    DATABASE_URL: your_database_url
    DEBUG: False
```

## Testing Environment Variables

To verify your environment variables are correctly set:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY', 'Not set'))"
```

## Security Considerations

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Rotate API keys regularly
- Use different API keys for development and production
- Restrict API key permissions to only what's needed
- Consider using a secrets manager for production deployments

## Troubleshooting

### Variables Not Loading

If environment variables aren't being loaded:

1. Verify the `.env` file is in the project root
2. Check for syntax errors (no spaces around `=`, no quotes)
3. Make sure `load_dotenv()` is called early in your application

### API Key Errors

If you're getting API authentication errors:

1. Verify the API keys are correct
2. Check for whitespace in the copied keys
3. Make sure the API service account is active and has sufficient credits

### Database Connection Issues

If database connection fails:

1. Check the `DATABASE_URL` format
2. Verify database server is running and accessible
3. Confirm user permissions are correct
