import sys
import os

# Add parent directory to path so we can import app_real_data
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_real_data import app

# Export for Vercel
app = app
