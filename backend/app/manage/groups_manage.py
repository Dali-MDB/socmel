from fastapi import APIRouter,Depends
from app.dependencies import SessionDep,Session
from app.models.messages import GroupChat
from typing import Annotated
from app.schemas.groups_schema import GroupChatCreate,GroupChatDisplay
from app.manage.security_manage import current_user
from app.authentication import oauth2_scheme
from fastapi.exceptions import HTTPException
from fastapi import status
from app.models.users import User
from app.schemas.users_schemas import UserDisplay
from app.manage.connection_manager import manager


groups_router = APIRouter(prefix='/groups',tags=['groups'])





@groups_router.post('/create/',response_model=GroupChatDisplay)
async def create_group(group:GroupChatCreate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    group_data = group.model_dump()
    #get the current user
    user = current_user(token,db)
    group_data['owner_id'] = user.id
    if user.id not in group_data['members']:
        group_data['members'].append(user.id)    #append the user to members list

    members_ids = group_data.pop('members')
    members = db.query(User).filter(User.id.in_(members_ids))
    group_db = GroupChat(**group_data)
    group_db.members.extend(members)
    db.add(group_db)
    db.commit()
    db.refresh(group_db)

    manager.add_user_to_group(user.id,group_db.id)   #add the user to the group in websockets
    
    return group_db

def fetch_group(group_id:int,db:Session):
    group = db.query(GroupChat).filter(GroupChat.id==group_id).first()
    if not group:
        raise HTTPException(404,'the group you are looking for does not exist')
    return group




@groups_router.get('/{group_id}/',response_model=GroupChatDisplay)
async def display_group(group_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    #verify permission (must be a members)
    if not user.id in [member.id for member in group.members]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not view this group')
    return group




@groups_router.get('/{group_id}/members/',response_model=list[UserDisplay])
async def get_group_members(group_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    if not user.id in group.members_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not view this group')
    return group.members



@groups_router.post('/{group_id}/add_member/{user_id}/',response_model=list[UserDisplay])
async def add_member(group_id:int,user_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    if not user.id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not add members to this group')
    member = db.query(User).filter(User.id==user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='the user you are looking for does not exist')
    if member.id not in group.members_ids:
        group.members.append(member)
    db.commit()
    db.refresh(group)

    manager.add_user_to_group(member.id,group.id)   #add the user to the group in websockets

    return group.members




@groups_router.delete('/{group_id}/remove_member/{user_id}/',response_model=list[UserDisplay])
async def remove_member(group_id:int,user_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    if not user.id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not remove members from this group')
    member = db.query(User).filter(User.id==user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='the user you are looking for does not exist')
    if member.id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not remove yourself from the group')
    if member.id in group.members_ids:
        group.members.remove(member)
    
    db.commit()
    db.refresh(group)

    manager.remove_user_from_group(member.id, group.id)    #remove the user from the group membersin webscokets
    return group.members



@groups_router.delete('/{group_id}/leave/',response_model=list[UserDisplay])
async def leave_group(group_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    if not user.id in group.members_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not leave this group')
    if user.id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not leave the group you own')
    group.members.remove(user)
    db.commit()
    db.refresh(group)
    manager.remove_user_from_group(user.id, group.id)    #remove the user from the group membersin webscokets
    return group.members


#an end point to pass owner ship to another user
@groups_router.put('/{group_id}/pass_ownership/{user_id}/',response_model=UserDisplay)
async def pass_ownership(group_id:int,user_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    group = fetch_group(group_id,db)
    if not user.id == group.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='you can not pass ownership of this group')
    member = db.query(User).filter(User.id==user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='the user you are looking for does not exist')
    if not member.id in group.members_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='this user is not a member of this group')
    group.owner_id = member.id
    db.commit()
    db.refresh(group)
    return member