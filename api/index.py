import os
import sys

# Ensure project root is available to Python import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel Serverless Function entry point
# 'app' is the FastAPI ASGI application instance
