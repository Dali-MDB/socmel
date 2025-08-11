from fastapi import WebSocket,APIRouter,WebSocketDisconnect
from app.manage.connection_manager import ConnectionManager
from app.authentication import current_user
from app.dependencies import get_db,SessionLocal,SessionDep
from typing import Dict,List
from app.models.messages import DmMessage
from fastapi import Depends
from app.authentication import oauth2_scheme
from typing import Annotated
from app.schemas.dm_messages_schemas import DmMessageDisplay



dm_router = APIRouter(prefix='/messages',tags=['messages'])
manager = ConnectionManager()

@dm_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = current_user(token,next(get_db()))


    await manager.connect(user.id,websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = data["message"]
            print(message)
            receiver_id = data["receiver_id"]
            db = SessionLocal()
    
            msg = DmMessage(  #create the message instance
                content = message,
                sender_id = user.id,
                recipient_id = receiver_id
            )
            db.add(msg)
            db.commit()
            await manager.send_direct_message(message, receiver_id)
    except WebSocketDisconnect:
        manager.disconnect(user.id)


@dm_router.get("/history/{receiver_id}/",response_model=List[DmMessageDisplay])
def get_chat_history(receiver_id: int, db: SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,next(get_db()))
    messages = db.query(DmMessage).filter(
        ((DmMessage.sender_id == user.id) & (DmMessage.recipient_id == receiver_id)) |
        ((DmMessage.sender_id == receiver_id) & (DmMessage.recipient_id == user.id))
    ).order_by(DmMessage.timestamp).all()

    return messages
