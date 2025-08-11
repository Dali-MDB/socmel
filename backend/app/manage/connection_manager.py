from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections : Dict[int,WebSocket] = {}   #a dictionnary for storing active users

    async def connect(self,user_id:int,websocket:WebSocket):
        await websocket.accept()  #wwit for connection
        self.active_connections[user_id] = websocket   #mark this user as active

    async def disconnect(self,user_id:int):
        self.active_connections.pop(user_id,None)

    async def send_direct_message(self, message: str, receiver_id: int):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_text(message)


