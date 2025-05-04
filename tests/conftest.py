import os
import sys
import pytest

# Add the project root directory to Python path
# This ensures that the 'app' module can be imported in tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))