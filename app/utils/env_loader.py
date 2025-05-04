import os
from dotenv import load_dotenv
import sys

# Flag to track if environment variables have been loaded
_env_loaded = False

def load_env():
    """
    Load environment variables from .env file if not already loaded
    """
    global _env_loaded
    
    if not _env_loaded:
        # Get the project root directory
        # If running from a script in a subdirectory, this will find the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = current_dir
        
        # Navigate up until we find the .env file or reach the filesystem root
        while not os.path.exists(os.path.join(project_root, '.env')) and project_root != os.path.dirname(project_root):
            project_root = os.path.dirname(project_root)
        
        # Check if .env file exists
        env_path = os.path.join(project_root, '.env')
        if os.path.exists(env_path):
            # Load the .env file
            load_dotenv(env_path)
            _env_loaded = True
            print(f"Environment variables loaded from {env_path}")
        else:
            print("Warning: .env file not found in project directory or any parent directory")
            print("Current directory:", current_dir)
            print("Searched up to:", project_root)
            
            # Check if we're running in a test environment
            if 'pytest' in sys.modules:
                print("Running in pytest environment, using default test values")
                # Set default test values
                os.environ.setdefault("TAVILY_API_KEY", "test_key")
                os.environ.setdefault("OPENAI_API_KEY", "test_key")
                os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
                os.environ.setdefault("DEBUG", "True")
                _env_loaded = True

# Load environment variables when the module is imported
load_env()