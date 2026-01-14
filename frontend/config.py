# rag_agent_app/frontend/config.py

import os
from dotenv import load_dotenv


def load_frontend_config():
    """
    Loads environment variables relevant to the frontend from the .env file.
    Assumes .env is in the project root (one level up from frontend/).

    For deployment:
    - Set FASTAPI_BASE_URL environment variable to your deployed backend URL
    - Example: https://medagent-heart-backend.onrender.com
    """
    load_dotenv()

    # Get backend URL from environment or default to localhost
    backend_url = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

    # Remove trailing slash if present
    backend_url = backend_url.rstrip("/")

    return {"FASTAPI_BASE_URL": backend_url}


# Load config once when the module is imported
FRONTEND_CONFIG = load_frontend_config()
