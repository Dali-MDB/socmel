from fastapi import WebSocket,APIRouter
from manage.connection_manager import ConnectionManager


room_router = APIRouter(prefix='/room')
manager = ConnectionManager()

@room_router.websocket('/ws/room/')
async def room_websocket_endpoint(websocket:WebSocket):
    room_id = websocket.query_params.get('room_id')