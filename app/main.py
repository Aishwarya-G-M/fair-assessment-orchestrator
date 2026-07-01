from dotenv import load_dotenv
load_dotenv()

import os
import threading
import httpx
from fastapi import FastAPI
from app.api.routes import router


def warm_fuji() -> None:
    base_url = os.getenv("FUJI_BASE_URL")
    username = os.getenv("FUJI_USERNAME")
    password = os.getenv("FUJI_PASSWORD")

    if not base_url:
        return

    try:
        httpx.post(
            f"{base_url.rstrip('/')}/evaluate",
            json={
                "object_identifier": "https://doi.org/10.1594/PANGAEA.902845",
                "test_debug": False,
            },
            auth=(username, password) if username and password else None,
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
    except Exception:
        pass


def create_app() -> FastAPI:
    application = FastAPI(
        title="FAIR Assessment Orchestrator",
        version="0.1.0",
    )
    application.include_router(router)

    @application.on_event("startup")
    def startup_event() -> None:
        threading.Thread(target=warm_fuji, daemon=True).start()

    return application


app = create_app()