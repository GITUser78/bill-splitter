from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from .routes import pages, api

app = FastAPI(title="Bill Splitter")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(api.router)
