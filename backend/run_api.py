import uvicorn

from backend.api.api import api
from backend.config.logging_config import setup_logging
from backend.config.settings import API_HOST, API_PORT

setup_logging()

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        api,
        host=API_HOST,
        port=API_PORT,
        reload=False
    )
