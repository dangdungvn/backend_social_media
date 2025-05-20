"""
Script để nếu daphne_asgi.py
"""

import os
import uvicorn
import sys

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Thu thập static files
if __name__ == "__main__":
    print("Starting ASGI server with Uvicorn...")

    # Run the application with uvicorn
    uvicorn.run(
        "backend.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto reload on file changes
        log_level="info",
    )
