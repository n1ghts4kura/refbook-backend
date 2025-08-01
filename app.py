# app.py
# The main entry point for the FastAPI application.
#

DEBUG = True

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from module.routes.answer import router as answer_router
from module.routes.book import router as book_router
from module.routes.user.router import router as user_router

from module.database.general import (
    get_book_database,
    get_chat_history_database,
    get_user_database,
    get_user_detail_database,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP

    get_book_database()
    get_chat_history_database()
    get_user_database()
    get_user_detail_database()

    yield

    # SHUTDOWN

    pass

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://refbookapi.s4kura.cc", ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(
        HTTPSRedirectMiddleware,
    )
]

app = FastAPI(
    debug=DEBUG,
    title="RefBook API",
    description="API for the RefBook application",
    version="1.0.0",
    on_startup=None,
    on_shutdown=None,
    middleware=middleware,
    lifespan=lifespan,
)

app.include_router(answer_router, prefix="/api/answer", tags=["Answer"])
app.include_router(book_router, prefix="/api/book", tags=["Book"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
