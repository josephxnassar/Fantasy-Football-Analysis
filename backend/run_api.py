from backend import config  # Imports and runs setup_logging() from __init__.py
from backend.api.api import api
from backend.config.settings import API_HOST, API_PORT
import uvicorn

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        api,
        host=API_HOST,
        port=API_PORT,
        reload=False
    )
