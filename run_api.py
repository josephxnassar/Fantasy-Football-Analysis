import config  # Required
import uvicorn

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "source.api:api",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on file changes during development
    )
