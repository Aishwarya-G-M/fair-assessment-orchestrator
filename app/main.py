from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import router

load_dotenv()

def create_app() -> FastAPI:
    application = FastAPI(
        title="FAIR Assessment Orchestrator",
        version="0.1.0",
    )
    application.include_router(router)
    return application


app = create_app()