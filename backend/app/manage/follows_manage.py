from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from app.dependencies import SessionDep
from app.authentication import oauth2_scheme, current_user
from app.models.users import User
from app.models.follows import Follow
from app.schemas.users_schemas import UserDisplay

follow_router = APIRouter(prefix='/follows', tags=['follows'])

def fetch_user(user_id: int, db: SessionDep):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Send a follow request
@follow_router.post('/request/{user_id}/')
async def request_follow(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    followed_user = db.query(User).filter(User.id == user_id).first()
    if not followed_user:
        raise HTTPException(404, 'This user does not exist')
    follow = db.query(Follow).filter(Follow.follower_id == user.id, Follow.followed_id == user_id).first()
    if follow:
        if follow.is_pending:
            raise HTTPException(400, 'Follow request already sent and pending')
        else:
            raise HTTPException(400, 'You are already following this user')
    follow = Follow(follower_id=user.id, followed_id=user_id)
    db.add(follow)
    db.commit()
    return {'detail': 'The follow request has been sent successfully'}

# View all my follow requests (pending requests to me)
@follow_router.get('/requests/', response_model=List[UserDisplay])
async def view_my_follow_requests(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    requests = db.query(Follow).filter(Follow.followed_id == user.id, Follow.is_pending == True).all()
    return [fetch_user(f.follower_id, db) for f in requests]

# View all my followers (accepted)
@follow_router.get('/followers/', response_model=List[UserDisplay])
async def view_my_followers(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    followers = db.query(Follow).filter(Follow.followed_id == user.id, Follow.is_pending == False).all()
    return [fetch_user(f.follower_id, db) for f in followers]

# View all the users I follow (accepted)
@follow_router.get('/following/', response_model=List[UserDisplay])
async def view_my_following(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    following = db.query(Follow).filter(Follow.follower_id == user.id, Follow.is_pending == False).all()
    return [fetch_user(f.followed_id, db) for f in following]

# Cancel follow request (sent by me, still pending)
@follow_router.delete('/request/{follow_id}/cancel/', status_code=200)
async def cancel_follow_request(follow_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    follow = db.query(Follow).filter(Follow.follower_id == user.id, Follow.id == follow_id, Follow.is_pending == True).first()
    if not follow:
        raise HTTPException(404, 'No pending follow request found')
    db.delete(follow)
    db.commit()
    return {'detail': 'Follow request cancelled'}

# Accept follow request (to me)
@follow_router.put('/request/{follow_id}/accept/', status_code=200)
async def accept_follow_request(follow_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    follow = db.query(Follow).filter(Follow.id == follow_id, Follow.followed_id == user.id).first()
    if not follow:
        raise HTTPException(404, 'No follow request found')
    if not follow.is_pending:
        raise HTTPException(status_code=400, detail='This follow request has already been accepted')
    follow.is_pending = False
    db.commit()
    return {'detail': 'Follow request accepted'}

# Reject follow request (to me)
@follow_router.delete('/request/{follow_id}/reject/', status_code=200)
async def reject_follow_request(follow_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    follow = db.query(Follow).filter(Follow.id == follow_id, Follow.followed_id == user.id, Follow.is_pending == True).first()
    if not follow:
        raise HTTPException(404, 'No pending follow request found')
    db.delete(follow)
    db.commit()
    return {'detail': 'Follow request rejected'}

# Unfollow endpoint (accepted follow only)
@follow_router.delete('/unfollow/{user_id}/', status_code=200)
async def unfollow_user(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    follow = db.query(Follow).filter(Follow.follower_id == user.id, Follow.followed_id == user_id, Follow.is_pending == False).first()
    if not follow:
        raise HTTPException(404, 'You are not following this user')
    db.delete(follow)
    db.commit()
    return {'detail': 'Unfollowed successfully'}

# Remove a follower (current user removes someone who follows them)
@follow_router.delete('/remove_follower/{user_id}/', status_code=200)
async def remove_follower(user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    follow = db.query(Follow).filter(Follow.id == user_id, Follow.followed_id == user.id, Follow.is_pending == False).first()
    if not follow:
        raise HTTPException(404, 'This user is not your follower')
    db.delete(follow)
    db.commit()
    return {'detail': 'Follower removed successfully'}
