# Technical Stack

## Backend Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI for high-performance API development
- **Agent Framework**: LangChain for orchestrating LLM workflows
- **Vector Database**: Pinecone for efficient similarity search
- **Document Processing**: Unstructured.io for medical document parsing
- **Search Integration**: 
  - Tavily API for medical research search
  - DuckDuckGo API for general web search
- **LLM Integration**: OpenAI API (GPT-4) with domain-specific fine-tuning

## Frontend Technologies
- **Framework**: Next.js with React
- **Mobile**: React Native for cross-platform mobile support
- **UI Components**: Tailwind CSS with custom medical-themed components
- **State Management**: Redux Toolkit
- **Authentication**: Auth0 with SAML for hospital SSO integration

## Infrastructure
- **Deployment**: Docker containers orchestrated with Kubernetes
- **Cloud Provider**: AWS (EKS, S3, RDS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus and Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

## Data Pipeline
- **ETL**: Apache Airflow for knowledge base updates
- **Data Validation**: Great Expectations
- **Data Storage**: 
  - PostgreSQL for relational data
  - MongoDB for document storage
  - Redis for caching

## Security
- **API Security**: OAuth 2.0 and JWT
- **Data Encryption**: AES-256 for data at rest
- **Compliance**: HIPAA-compliant infrastructure
- **Vulnerability Scanning**: Snyk and OWASP ZAP