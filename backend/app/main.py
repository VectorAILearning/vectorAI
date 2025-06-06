import logging
import sys
from contextlib import asynccontextmanager

from api.v1.router import api_v1_router
from api.v1.websocket import router as websocket_router
from core.arq import get_arq_pool
from core.broadcast import broadcaster
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broadcaster.connect()
    app.state.arq_pool = await get_arq_pool()
    yield
    await app.state.arq_pool.close()
    await broadcaster.disconnect()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)
app.include_router(websocket_router)
