from fastapi import FastAPI
import contextlib

from middleware.jwt_middleware import JWTMiddleware
from core.db.base import init_db
from api.v1.endpoints.agent_builders import router as create_agent_router
from api.public.meta import router as public_meta_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Agent Builder Server", lifespan=lifespan)

app.include_router(public_meta_router, prefix="/api")

# app.add_middleware(
#     JWTMiddleware,
#     jwks_url="https://dev.arealtimetech.com/idp/.well-known/jwks.json",
#     audience="agent-builder",
#     issuer="https://dev.arealtimetech.com/idp"
# )

app.include_router(create_agent_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002)
