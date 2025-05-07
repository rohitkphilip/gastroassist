# Technical Stack

## Backend Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI for high-performance API development
- **Agent Framework**: LangChain for orchestrating LLM workflows
- **Vector Database**: Pinecone for efficient similarity search
- **Document Processing**: Unstructured.io for medical document parsing
- **Search and Extraction**: 
  - Tavily API for both search and content extraction
  - DuckDuckGo API as backup search engine
- **LLM Integration**: 
  - OpenAI API (GPT-3.5 Turbo) for efficient summarization
  - Optimized with medical-specific prompting

## Frontend Technologies
- **Framework**: Next.js with React
- **Language**: TypeScript for type safety
- **Component Library**: React functional components
- **Styling**: Tailwind CSS with custom medical-themed components
- **State Management**: Redux with Redux Toolkit
- **API Integration**: Axios for HTTP requests
- **Loading States**: Custom loading indicators

## Infrastructure
- **Deployment**: Docker containers
- **Local Development**: Python venv + npm
- **Configuration**: Environment variables via .env file
- **Database**: 
  - SQLite (development)
  - PostgreSQL (production)

## Enhanced Pipeline Components
- **Query Processing**: Custom NLP with medical term recognition
- **Knowledge Retrieval**:
  - Tavily Search: Configured for medical domain search
  - Tavily Extract: Using Search API with raw content extraction
- **Summarization**:
  - GPT-3.5 Turbo: Optimized for efficiency and cost
  - Medical Prompting: Specialized instructions for medical content
  - Error Handling: Multi-tiered fallback mechanisms

## Testing Framework
- **Unit Testing**: pytest for backend components
- **Integration Testing**: Custom test scripts
- **Manual Testing**: Pre-defined gastroenterology questions
- **Test Data**: Curated medical queries with expected answers

## Security
- **API Security**: Authentication headers
- **Data Encryption**: HTTPS for data in transit
- **Error Handling**: Sanitized error messages
- **Input Validation**: Request validation with Pydantic
