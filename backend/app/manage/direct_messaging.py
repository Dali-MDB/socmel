from fastapi import WebSocket,APIRouter,WebSocketDisconnect
from app.manage.connection_manager import AdvancedConnectionManager
from app.authentication import current_user
from app.dependencies import get_db,SessionLocal,SessionDep
from typing import Dict,List
from app.models.messages import DmMessage,GroupChat,GroupChatMessage
from fastapi import Depends
from app.authentication import oauth2_scheme
from typing import Annotated
from app.schemas.dm_messages_schemas import DmMessageDisplay,GroupMesssageDisplay
from app.manage.groups_manage import fetch_group
from fastapi.exceptions import HTTPException
from app.schemas.dm_messages_schemas import GroupMesssageDisplay




messages_router = APIRouter(prefix='/messages',tags=['messages'])
manager = AdvancedConnectionManager()

@messages_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,token:str):
    db = SessionLocal()
    user = current_user(token,next(get_db()))
    #we fetch all user's groups
    groups = db.query(GroupChat).filter(GroupChat.members.any(id=user.id)).all()
    groups = [g.id for g in groups]
    print(user.id)
    await manager.connect(user.id,websocket,groups)

    try:

        while True:
            data = await websocket.receive_json()
            if data.get('type') and data['type'] == 'dm':
                message = data["message"]
        
                receiver_id = int(data["receiver_id"])
                db = SessionLocal()
        
                msg = DmMessage(  #create the message instance
                    content = message,
                    sender_id = user.id,
                    recipient_id = receiver_id
                )
                db.add(msg)
                db.commit()

                msg = DmMessageDisplay.model_validate(msg)
                await manager.send_direct_message(message,user.id,receiver_id,msg)
            elif data.get('type') and data['type'] == 'group':
                message = data["message"]

                group_id = int(data["group_id"])
                parent_id = data.get('parent_id',None) 
                parent_id = int(parent_id) if parent_id else None
                db = SessionLocal()

                msg = GroupChatMessage(
                    content = message,
                    sender_id = user.id,
                    group_chat_id = group_id,
                    parent_message_id = parent_id
                )
                db.add(msg)
                db.commit()
            
                msg = GroupMesssageDisplay.model_validate(msg)
                
                await manager.send_group_message(message,group_id,user.id,msg)
    except WebSocketDisconnect:
        manager.disconnect(user.id)


@messages_router.get("/history/dm/{receiver_id}/",response_model=List[DmMessageDisplay])
def get_chat_history(receiver_id: int, db: SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,next(get_db()))
    messages = db.query(DmMessage).filter(
        ((DmMessage.sender_id == user.id) & (DmMessage.recipient_id == receiver_id)) |
        ((DmMessage.sender_id == receiver_id) & (DmMessage.recipient_id == user.id))
    ).order_by(DmMessage.timestamp).all()

    return messages

@messages_router.get('/history/group/{group_id}/',response_model=List[GroupMesssageDisplay])
def get_group_chat_history(group_id:int,db: SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,next(get_db()))
    group = fetch_group(group_id,db)
    if not user.id in group.members_ids:
        raise HTTPException(status_code=403,detail='you are not a member of this group chat')
    messages = db.query(GroupChatMessage).filter(GroupChatMessage.group_chat_id == group_id).order_by(GroupChatMessage.timestamp).all()
    
    return messages

