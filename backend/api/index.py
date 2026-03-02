"""Vercel serverless entry point — re-exports the FastAPI app."""

import sys
import os

# Ensure the backend root is in the Python path so `app.*` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402, F401
