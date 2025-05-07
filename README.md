# GastroAssist AI

GastroAssist is an intelligent Q&A system designed specifically for gastroenterologists. This system combines curated medical knowledge with real-time information retrieval to provide concise, source-traced answers to clinical questions.

![GastroAssist Logo](https://via.placeholder.com/500x150?text=GastroAssist+AI)

## 🌟 Key Features

- **Dual knowledge sources**: Combines a curated gastroenterology knowledge base with dynamic search
- **Source traceability**: All information includes proper citation for clinical confidence
- **Intelligent query processing**: Understands medical terminology and the intent behind clinical questions
- **Web and mobile interfaces**: Access from any device for seamless integration into clinical workflow

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, please ensure you have the following installed:

- Python 3.11+ ([Download Python](https://www.python.org/downloads/))
- Node.js 18+ ([Download Node.js](https://nodejs.org/))
- Git ([Download Git](https://git-scm.com/downloads))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Suryam1976/gastroassist.git
   cd gastroassist
   ```

2. **Set up the backend**

   ```bash
   # Create and activate virtual environment
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```
   # API Keys - Get these from your account dashboards
   OPENAI_API_KEY=your_openai_api_key  # Get from: https://platform.openai.com/api-keys
   TAVILY_API_KEY=your_tavily_api_key  # Get from: https://tavily.com/dashboard

   # Database
   DATABASE_URL=sqlite:///./gastroassist.db

   # Server
   DEBUG=True
   ```

4. **Start the backend server**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Set up the frontend** (in a new terminal window)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**

   - Web interface: [http://localhost:3000](http://localhost:3000)
   - API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - API health check: [http://localhost:8000](http://localhost:8000)

## 📚 Documentation

For more detailed information, please refer to:

- [System Architecture](./docs/architecture/system-overview.md)
- [Development Setup Guide](./docs/development/setup-guide.md)
- [Testing Guide](./docs/development/testing-guide.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: Next.js, React, TypeScript
- **Knowledge Base**: Pinecone Vector Database
- **Search Integration**: Tavily, DuckDuckGo
- **LLM**: OpenAI GPT-4

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/development/contributing.md) for more details.

## 📞 Need Help?

If you encounter any issues:

1. Check the [Troubleshooting Guide](./docs/troubleshooting.md)
2. Search for similar issues in our [GitHub repository](https://github.com/your-organization/gastroassist/issues)
3. Join our [Discord community](https://discord.gg/gastroassist) for developer support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
