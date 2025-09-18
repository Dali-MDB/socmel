from fastapi import FastAPI
from fastapi import Request
from app.database import engine
from app import models
from contextlib import asynccontextmanager

from app.authentication import auth_router
from app.manage.posts_manage import posts_router
from app.manage.spaces_manage import spaces_router
from app.manage.users_manage import users_router
from app.manage.security_manage import sec_auth
from app.manage.follows_manage import follow_router
from app.manage.direct_messaging import messages_router
from app.manage.groups_manage import groups_router
from app.manage.notes_manage import notes_router
from app.tasks.tasks import scheduler

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

import cloudinary
import cloudinary.uploader
import cloudinary.api

import os
import dotenv

dotenv.load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET')
)

@asynccontextmanager
async def lifespan(app:FastAPI):
 #   models.Base.metadata.create_all(bind=engine)
    scheduler.start()
    print("scheduler started")
    yield
    scheduler.shutdown()
    print("scheduler stopped")




app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(spaces_router)
app.include_router(users_router)
app.include_router(sec_auth)
app.include_router(follow_router)
app.include_router(messages_router)
app.include_router(groups_router)
app.include_router(notes_router)


def user_key_fct( request: Request):
    client_ip = request.client.host
    if request.state.is_authenticated:
        return request.state.cur_user
    return  client_ip
limiter = Limiter(key_func=user_key_fct)
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)





@app.get('/limit')
@limiter.limit('2/minute')
def test_limit(request:Request):
    return {'gg':'gg'}

from app.middlewares.auth_middleware import get_auth_details
app.middleware("http")(get_auth_details)

