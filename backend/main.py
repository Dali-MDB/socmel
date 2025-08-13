from fastapi import FastAPI
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

@asynccontextmanager
async def lifespan(app:FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(spaces_router)
app.include_router(users_router)
app.include_router(sec_auth)
app.include_router(follow_router)
app.include_router(messages_router)
app.include_router(groups_router)

'''

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    websocket.accept()
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


'''