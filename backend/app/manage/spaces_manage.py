from fastapi import APIRouter
from app.models.spaces import Space,Room,SpaceInvitation
from app.models.users import User
from app.schemas.spaces_schemas import SpaceCreate,SpaceUpdate,SpaceDisplay
from app.schemas.rooms_schemas import RoomCreate, RoomUpdate, RoomDisplay
from app.schemas.invitations_schemas import InvitationCreate, InvitationDisplay
from app.authentication import oauth2_scheme,current_user
from app.dependencies import SessionDep
from typing import Annotated
from fastapi import Depends,HTTPException,status,Body
from datetime import datetime
from app.schemas.users_schemas import UserDisplay


spaces_router = APIRouter(prefix='/spaces',tags=['spaces'])





@spaces_router.post('/create',response_model=SpaceDisplay)
async def create_space(space:SpaceCreate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    #we check if the space name is already taken
    if db.query(Space).filter(Space.name == space.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Space name already taken")
    
    space_data = space.model_dump()
    space_data['owner_id'] = user.id
    space = Space(**space_data)
    #we create a main room for the space
    room = Room(name="main",space_id=space.id)
    db.add(space)
    db.add(room)
    db.commit()
    db.refresh(space)
    db.refresh(room)
    #add the owner to the space
    space.members.append(user)
    db.commit()
    return space


def fetch_space(space_id:int,db:SessionDep):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Space not found")
    return space


def has_space_permission(space:Space,user:User):
    return space.owner_id == user.id

@spaces_router.put('/{space_id}/edit/',response_model=SpaceDisplay)
async def edit_space(space_id:int,space:SpaceUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space_db = fetch_space(space_id,db)
    if not has_space_permission(space_db,user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of this space")
    #check if the new name is already taken
    if db.query(Space).filter(Space.name == space.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Space name already taken")
    space_data = space.model_dump(exclude_unset=True)
    for key,value in space_data.items():
        setattr(space_db,key,value)
    db.commit()
    db.refresh(space_db)
    return space


@spaces_router.delete('/{space_id}/delete/',status_code=status.HTTP_200_OK)
async def delete_space(space_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    if not has_space_permission(space,user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of this space")
    db.delete(space)
    db.commit()
    return {"message": "Space deleted"}



@spaces_router.get('/{space_id}/view/',response_model=SpaceDisplay)
async def view_space(space_id:int,db:SessionDep):
    space = fetch_space(space_id,db)
    return space



@spaces_router.post('/{space_id}/rooms/add/',response_model=RoomDisplay)
async def add_room(space_id:int,room:RoomCreate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    if not has_space_permission(space,user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of this space")
    #query a room with the same name in the space
    if db.query(Room).filter(Room.name == room.name,Room.space_id == space.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Room name already taken")
    room_data = room.model_dump()
    room_data['space_id'] = space.id
    room = Room(**room_data)
    db.add(room)
    db.commit()
    db.refresh(room)

def fetch_room(room_id: int,space_id:int, db: SessionDep):
    room = db.query(Room).filter(Room.id == room_id,Room.space_id == space_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@spaces_router.put('/{space_id}/rooms/{room_id}/edit/', response_model=RoomDisplay)
async def edit_room(space_id: int, room_id: int, room: RoomUpdate, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    space = fetch_space(space_id, db)
    if not has_space_permission(space, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this space")
    room_db = fetch_room(room_id,space_id, db)
    if room_db.space_id != space.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room does not belong to this space")
    # Check if the new name is already taken in this space
    if room.name and db.query(Room).filter(Room.name == room.name, Room.space_id == space.id, Room.id != room_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room name already taken")
    room_data = room.model_dump(exclude_unset=True)
    for key, value in room_data.items():
        setattr(room_db, key, value)
    db.commit()
    db.refresh(room_db)
    return room_db


@spaces_router.delete('/{space_id}/rooms/{room_id}/delete/', status_code=status.HTTP_200_OK)
async def delete_room(space_id: int, room_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    space = fetch_space(space_id, db)
    if not has_space_permission(space, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this space")
    room_db = fetch_room(room_id,space_id, db)
    db.delete(room_db)
    db.commit()
    return {"message": "Room deleted"}



@spaces_router.get('/{space_id}/rooms/{room_id}/view/', response_model=RoomDisplay)
async def view_room(space_id: int, room_id: int, db: SessionDep):
    room_db = fetch_room(room_id,space_id, db)
    return room_db


import uuid
@spaces_router.post('/{space_id}/invitations/create/',response_model=InvitationDisplay)
async def create_invitation(space_id:int,invitation:InvitationCreate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    #the user needs to be a member of the space
    if user not in space.members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this space")
    
    invitation = SpaceInvitation(
        space_id=space.id,
        max_uses=invitation.max_uses,
        expires_at=invitation.expires_at,
        token=str(uuid.uuid4())
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation   


@spaces_router.get('/{space_id}/invitations/join/{invitation_token}/',status_code=status.HTTP_200_OK)
async def join_space(space_id:int,invitation_token:str,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    invitation = db.query(SpaceInvitation).filter(SpaceInvitation.token == invitation_token,SpaceInvitation.space_id == space.id).first()
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invitation not found")
    if invitation.expires_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invitation has expired")
    if invitation.max_uses <= invitation.current_uses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invitation has reached the maximum number of uses")
    if user in space.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are already a member of this space")
    
    #add the user to the space
    space.add_member(user)
    db.commit()
    return {"message": "You have joined the space"}


@spaces_router.get('/{space_id}/members/all/',response_model=list[UserDisplay])
async def get_space_members(space_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    if not user in space.members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a member of this space")
    return space.members


@spaces_router.delete('/{space_id}/members/{user_id}/remove/',status_code=status.HTTP_200_OK)
async def remove_member(space_id:int,user_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    if not has_space_permission(space,user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not the owner of this space")
    member = db.query(User).filter(User.id == user_id).first()
    if not member or not member in space.members :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Member not found")
    space.remove_member(member)
    db.commit()
    return {"message": "Member removed"}


  