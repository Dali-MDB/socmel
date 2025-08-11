from fastapi import Depends,APIRouter, Body
from app.dependencies import SessionDep,Session
from app.models.posts import Post,Like,Comment,Reaction
from app.schemas.comments_schemas import CommentDisplay
from app.models.users import User
from app.schemas.posts_schemas import PostCreate,PostDisplay,PostUpdate
from app.authentication import oauth2_scheme,current_user
from typing import Annotated
from fastapi.exceptions import HTTPException
from fastapi import status,Response
from app.manage.spaces_manage import fetch_space

posts_router = APIRouter(prefix='/posts',tags=['posts'])



@posts_router.post('/create/',response_model=PostDisplay)
async def create_post_account(post:PostUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    post_data = post.model_dump()
    post_data['user_id'] = user.id
    post_db = Post(**post_data)
    db.add(post_db)
    db.commit()
    db.refresh(post_db)
    return post_db


@posts_router.post('/space/{space_id}/create/',response_model=PostDisplay)
async def create_post_account(space_id:int,post:PostUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    space = fetch_space(space_id,db)
    post_data = post.model_dump()
    post_data['user_id'] = user.id
    post_data['space_id'] = space.id
    post_data['for_space'] = True
    post_db = Post(**post_data)
    db.add(post_db)
    db.commit()
    db.refresh(post_db)
    return post_db


def fetch_post(post_id:int,db:Session):
    post = db.query(Post).filter(Post.id==post_id).first()
    if not post:
        raise HTTPException(status_code=404,detail='the post you are looking for does not exist')
    return post

def has_post_permission(post:Post,user:User):
    return post.user_id == user.id


@posts_router.get('/{post_id}/view/',response_model=PostDisplay)
async def view_post(post_id:int,db:SessionDep):
    post = fetch_post(post_id,db)
    return post



@posts_router.put('/{post_id}/edit/',response_model=PostDisplay)
async def edit_post(post_id:int,post:PostUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    post_db = fetch_post(post_id,db)
    user = current_user(token,db)
    if not has_post_permission(post_db,user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='you do not have permission to edit this post')
    
    post_data = post.model_dump(exclude_unset=True)
    for key,val in post_data.items():
        setattr(post_db,key,val)

    db.commit()
    db.refresh(post_db)
    return post_db


@posts_router.delete('/{post_id}/delete/',status_code=status.HTTP_200_OK)
async def delete_post(post_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    post_db = fetch_post(post_id,db)
    user = current_user(token,db)
    if not has_post_permission(post_db,user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='you do not have permission to edit this post')
    
    db.delete(post_db)
    db.commit()
    return {'detail':'the post has been deleted successfully'}



@posts_router.post('/{post_id}/like/')
async def like_post(post_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    post_db = fetch_post(post_id,db)
    user = current_user(token,db)
    
    #check if the user already likes this post
    old_like =  db.query(Like).filter(Like.post_id == post_id,Like.user_id == user.id).first()
    if old_like:  #unlike
        db.delete(old_like)
        post_db.likes_nbr-=1 
        liked = False
    else:  #like
        like = Like(post_id=post_id,user_id=user.id)
        db.add(like)
        post_db.likes_nbr+=1
        liked = True
    db.commit()
    like_count = post_db.likes_nbr
    return {
        'liked' : liked,
        'like_count' : like_count
    }
    


#add an end point to add a comment to a post
@posts_router.post('/{post_id}/comment/add/',response_model=CommentDisplay)
async def add_comment(post_id:int,comment:str,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    post_db = fetch_post(post_id,db)
    user = current_user(token,db)
    comment_db = Comment(content=comment,user_id=user.id,post_id=post_db.id)
    db.add(comment_db)
    db.commit()
    db.refresh(comment_db)
    return comment_db

#add an end point to add a comment to a post
@posts_router.post('/{post_id}/comment/add_reply/{comment_id}/',response_model=CommentDisplay)
async def add_reply(post_id:int,comment_id:int,reply:str,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    post_db = fetch_post(post_id,db)
    user = current_user(token,db)
    comment_old = db.query(Comment).filter(Comment.id==comment_id).first()
    if not comment_old:
        raise HTTPException(404,detail='this comment does not exist')
    comment_db = Comment(content=reply,user_id=user.id,post_id=post_db.id,parent_id=comment_id)
    db.add(comment_db)
    db.commit()
    db.refresh(comment_db)
    return comment_db



@posts_router.put('/{post_id}/comment/{comment_id}/edit/',response_model=CommentDisplay)
async def edit_comment(post_id:int,comment_id:int,new_comment:str,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    comment = db.query(Comment).filter(Comment.id==comment_id,Comment.post_id==post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail='Comment not found')
    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You do not have permission to edit this comment')
    comment.content = new_comment
    db.commit()
    db.refresh(comment)
    return comment


@posts_router.delete('/{post_id}/comment/{comment_id}/delete/',status_code=status.HTTP_200_OK)
async def delete_comment(post_id:int, comment_id:int, token:Annotated[str,Depends(oauth2_scheme)], db:SessionDep):
    user = current_user(token,db)
    comment = db.query(Comment).filter(Comment.id==comment_id,Comment.post_id==post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail='Comment not found')
    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You do not have permission to delete this comment')
    db.delete(comment)
    db.commit()
    return {"detail": "The comment has been deleted successfully"}


    
        
@posts_router.get('/{post_id}/comment/all',response_model=list[CommentDisplay])
async def get_post_comments(post_id:int,db:SessionDep):
    post = fetch_post(post_id,db)
    comments = db.query(Comment).filter(Comment.post_id == post_id)
    return comments




@posts_router.post('/{post_id}/comment/{comment_id}/react/')
def react_to_comment(post_id:int,comment_id:int, token:Annotated[str,Depends(oauth2_scheme)], db:SessionDep,reaction_type : str = Body(...)):
    comment = db.query(Comment).filter(Comment.post_id == post_id,Comment.id == comment_id).first()
    user = current_user(token,db)
    if not comment:
        raise HTTPException(404,'this comment does not exist')
    
    reaction = db.query(Reaction).filter(Reaction.comment_id == comment_id, Reaction.user_id == user.id, Reaction.reaction_type == reaction_type).first()
    if reaction:   #unreact
        db.delete(reaction)
        db.commit()
        return {"message": "Reaction removed", "reacted": False}
    else:
        reaction = Reaction(user_id = user.id, comment_id = comment_id,reaction_type=reaction_type)
        db.add(reaction)
        db.commit()
        return {"message": "Reaction added", "reacted": True}

        

    
# Get posts of a user (not for space)
@posts_router.get('/user/{user_id}/all/', response_model=list[PostDisplay])
async def get_user_posts(user_id: int, db: SessionDep):
    posts = db.query(Post).filter(Post.user_id == user_id, Post.for_space == False).all()
    return posts

# Get posts of a space (restrict access to members)
@posts_router.get('/space/{space_id}/all/', response_model=list[PostDisplay])
async def get_space_posts(space_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    space = fetch_space(space_id, db)
    if user not in space.members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this space")
    posts = db.query(Post).filter(Post.space_id == space_id, Post.for_space == True).all()
    return posts

# Get posts of a user in a space (restrict access to members)
@posts_router.get('/space/{space_id}/user/{user_id}/all/', response_model=list[PostDisplay])
async def get_user_posts_in_space(space_id: int, user_id: int, token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    user = current_user(token, db)
    space = fetch_space(space_id, db)
    if user not in space.members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this space")
    # Check if the owner exists
    owner = db.query(User).filter(User.id == user_id).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    posts = db.query(Post).filter(Post.space_id == space_id, Post.user_id == user_id, Post.for_space == True).all()
    return posts