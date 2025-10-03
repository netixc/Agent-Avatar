import os
import shutil
import asyncio
from typing import Optional

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from loguru import logger

from .routes import init_client_ws_route, init_webtool_routes
from .service_context import ServiceContext
from .config_manager.utils import Config
from .agent_zero_client import init_agent_zero_client


class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if path.endswith(".js"):
            response.headers["Content-Type"] = "application/javascript"
        return response


class AvatarStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        allowed_extensions = (".jpg", ".jpeg", ".png", ".gif", ".svg")
        if not any(path.lower().endswith(ext) for ext in allowed_extensions):
            return Response("Forbidden file type", status_code=403)
        return await super().get_response(path, scope)


class WebSocketServer:
    def __init__(self, config: Config):
        self.app = FastAPI()
        self.config = config
        self.ws_handler = None

        # Add CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize Agent-Zero client (always enabled for Agent-Zero only setup)
        agent_zero_url = config.system_config.agent_zero_url
        agent_zero_context = config.system_config.agent_zero_context_id

        init_agent_zero_client(
            base_url=agent_zero_url,
            context_id=agent_zero_context,
            enabled=True
        )

        # Load configurations and initialize the default context cache
        default_context_cache = ServiceContext()
        default_context_cache.load_from_config(config)

        # Include routes
        client_router, ws_handler = init_client_ws_route(default_context_cache=default_context_cache)
        self.ws_handler = ws_handler

        self.app.include_router(client_router)
        self.app.include_router(
            init_webtool_routes(default_context_cache=default_context_cache),
        )

        # Mount cache directory first (to ensure audio file access)
        if not os.path.exists("cache"):
            os.makedirs("cache")
        self.app.mount(
            "/cache",
            StaticFiles(directory="cache"),
            name="cache",
        )

        # Mount static files
        self.app.mount(
            "/assets/live2d-models",
            StaticFiles(directory="assets/live2d-models"),
            name="live2d-models",
        )
        self.app.mount(
            "/assets/backgrounds",
            StaticFiles(directory="assets/backgrounds"),
            name="backgrounds",
        )
        self.app.mount(
            "/bg",
            StaticFiles(directory="assets/backgrounds"),
            name="bg",
        )
        self.app.mount(
            "/assets/avatars",
            AvatarStaticFiles(directory="assets/avatars"),
            name="avatars",
        )

        # Mount main frontend last (as catch-all)
        self.app.mount(
            "/",
            CustomStaticFiles(directory="frontend", html=True),
            name="frontend",
        )

    def run(self):
        pass

    @staticmethod
    def clean_cache():
        """Clean the cache directory by removing and recreating it."""
        cache_dir = "cache"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)
