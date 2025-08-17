from fastapi import WebSocket
from typing import Dict
from datetime import datetime



class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}   #a dictionary for storing active users

    async def connect(self,user_id:int,websocket:WebSocket):
        await websocket.accept()  #wwit for connection
        self.active_connections[user_id] = websocket   #mark this user as active

    async def disconnect(self,user_id:int):
        self.active_connections.pop(user_id,None)

    async def send_direct_message(self, message: str, receiver_id: int):
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            await websocket.send_text(message)


from fastapi import WebSocket
from typing import Dict, Set, List, Optional

class AdvancedConnectionManager:
    def __init__(self) -> None:
        # Store active connections: user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        
        # Store group memberships: group_id -> set of user_ids
        self.group_members: Dict[int, Set[int]] = {}
        
        # Store user's groups: user_id -> set of group_ids (for quick lookup)
        self.user_groups: Dict[int, Set[int]] = {}


    
    async def connect(self, user_id: int, websocket: WebSocket, user_groups: List[int] = None):
        """
        Connect a user and register them to their groups
        
        Args:
            user_id: The user's ID
            websocket: The WebSocket connection
            user_groups: List of group IDs the user belongs to (fetch from database)
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Register user to their groups
        if user_groups:
            self.user_groups[user_id] = set(user_groups)
            for group_id in user_groups:
                if group_id not in self.group_members:
                    self.group_members[group_id] = set()
                self.group_members[group_id].add(user_id)


    
    async def disconnect(self, user_id: int):
        """Disconnect user and remove from all groups"""
        # Remove from active connections
        self.active_connections.pop(user_id, None)
        
        # Remove from all groups
        if user_id in self.user_groups:
            for group_id in self.user_groups[user_id]:
                if group_id in self.group_members:
                    self.group_members[group_id].discard(user_id)
                    # Clean up empty groups
                    if not self.group_members[group_id]:
                        del self.group_members[group_id]
            del self.user_groups[user_id]
    
    async def send_direct_message(self, message: str,sender_id:int, receiver_id: int, msg: None):
        """Send a direct message to a specific user"""
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            try:
                msg = msg.model_dump()
                msg['timestamp'] = msg['timestamp'].isoformat()
                await websocket.send_json(msg)
            except:
                # Connection might be broken, clean up
                await self.disconnect(receiver_id)
                

    async def send_group_message(self, message: str, group_id: int, sender_id: Optional[int] = None,msg=None):
        """
        Send a message to all members of a group
        
        Args:
            message: The message to send
            group_id: The group ID
            sender_id: ID of the sender (optional, to exclude from receiving the message)
        """
        if group_id not in self.group_members:
            return 
        
        msg = msg.model_dump()
        msg['timestamp'] = msg['timestamp'].isoformat()
        for user_id in self.group_members[group_id].copy():  # Copy to avoid modification during iteration
            # Skip sender if specified
            if sender_id and user_id == sender_id:
                continue
                
            if user_id in self.active_connections:
                
                try:
    
                    websocket = self.active_connections[user_id]
                    await websocket.send_json(data=msg)
                except:
                    # Connection broken, clean up
                    await self.disconnect(user_id)
        
       
    
    def add_user_to_group(self, user_id: int, group_id: int):
        """Add a user to a group (call this when user joins a new group)"""
        if group_id not in self.group_members:
            self.group_members[group_id] = set()
        
        if user_id not in self.user_groups:
            self.user_groups[user_id] = set()
        
        self.group_members[group_id].add(user_id)
        self.user_groups[user_id].add(group_id)
    
    def remove_user_from_group(self, user_id: int, group_id: int):
        """Remove a user from a group"""
        if group_id in self.group_members:
            self.group_members[group_id].discard(user_id)
            if not self.group_members[group_id]:   #clear if empty
                del self.group_members[group_id]
        
        if user_id in self.user_groups:
            self.user_groups[user_id].discard(group_id)
            if not self.user_groups[user_id]:     #clear if empty
                del self.user_groups[user_id]
    
    def get_group_members(self, group_id: int) -> List[int]:
        """Get all members of a group"""
        return list(self.group_members.get(group_id, set()))
    
    def get_user_groups(self, user_id: int) -> List[int]:
        """Get all groups a user belongs to"""
        return list(self.user_groups.get(user_id, set()))
    
    def get_active_users_in_group(self, group_id: int) -> List[int]:
        """Get only the currently connected users in a group"""
        if group_id not in self.group_members:
            return []
        
        return [user_id for user_id in self.group_members[group_id] 
                if user_id in self.active_connections]

