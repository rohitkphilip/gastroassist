# Getting Started with GastroAssist AI

This guide will help you set up and run the GastroAssist AI system on your local machine, even if you're new to web development.

## Prerequisites

Before you begin, make sure you have the following installed:

- [Python 3.11+](https://www.python.org/downloads/) - For the backend
- [Node.js 18+](https://nodejs.org/) - For the frontend
- [Git](https://git-scm.com/downloads) - For version control

## Step 1: Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/your-organization/gastroassist-ai.git
cd gastroassist-ai
```

## Step 2: Set Up the Backend

### Create a Python Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the root directory:

```
# API Keys
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key

# Database
DATABASE_URL=sqlite:///./gastroassist.db

# Server
DEBUG=True
```

Replace `your_openai_api_key` and `your_tavily_api_key` with your actual API keys.

### Start the Backend Server

```bash
# Start the development server
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

## Step 3: Set Up the Frontend

Open a new terminal window (keep the backend running) and navigate to the project folder.

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Start the Frontend Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Step 4: Access the Application

Open your web browser and go to:
- http://localhost:3000 - For the web interface
- http://localhost:8000/docs - For the API documentation

## Common Issues and Solutions

### "Module not found" errors
Make sure you've activated your virtual environment and installed all dependencies.

### API key errors
Double-check that your `.env` file contains the correct API keys.

### Port already in use
If port 8000 or 3000 is already in use, you can specify a different port:
```bash
# For backend
uvicorn app.main:app --reload --port 8001

# For frontend
npm run dev -- --port 3001
```

## Next Steps

- Check out the [System Architecture](./architecture/system-overview.md) to understand how the system works
- Read the [Testing Guide](./development/testing-guide.md) to learn how to test your changes
- Explore the [API Documentation](http://localhost:8000/docs) to understand available endpoints

## Getting Help

If you encounter any issues, please:
1. Check the [Troubleshooting Guide](./troubleshooting.md)
2. Search for similar issues in our GitHub repository
3. Ask for help in our developer Discord channel