from fastapi import APIRouter
from app.schemas.users_schemas import UserDisplay,UserUpdate
from app.authentication import oauth2_scheme,current_user
from app.dependencies import SessionDep
from fastapi import Depends,HTTPException,status
from typing import Annotated
from app.models.users import User,Follow
from app.dependencies import SessionDep
from fastapi import UploadFile
import cloudinary.uploader

users_router = APIRouter(prefix='/users',tags=['users'])


def fetch_user(user_id:int,db:SessionDep):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    return user

@users_router.get('/{user_id}/view/',response_model=UserDisplay)
async def view_user(user_id:int,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = fetch_user(user_id,db)
    return user



@users_router.get('/me/',response_model=UserDisplay)
async def view_me(token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    return user


@users_router.put('/me/',response_model=UserDisplay)
async def edit_me(user:UserUpdate,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user_db = current_user(token,db)
    user_data = user.model_dump(exclude_unset=True)
    for key,value in user_data.items():
        setattr(user_db,key,value)
    db.commit()
    db.refresh(user_db)
    return user


@users_router.post('/pfp/',response_model=UserDisplay)
async def upload_pfp(image:UploadFile,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
#check type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        #check if the user already have a pfp
        if user.pfp and user.pfp_public_id:
            cloudinary.uploader.destroy(user.pfp_public_id)
        upload_result = cloudinary.uploader.upload(
            image.file,
            folder="socmel/pfps",
            public_id=f"user_{user.id}_pfp",
            overwrite=True
        )
        
        # 4. Get the URL and update user
        profile_picture_url = upload_result.get("secure_url")
        user.pfp = profile_picture_url
        user.pfp_public_id = upload_result.get("public_id")
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")



@users_router.delete('/pfp/',response_model=UserDisplay)
async def remove_pfp(token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    if user.pfp:
        destroy_result = cloudinary.uploader.destroy(user.pfp_public_id, invalidate=True  
        )
    
            
        # Check if Cloudinary deletion was successful
        if destroy_result.get('result') != 'ok':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete image from Cloudinary: {destroy_result}"
            )
        user.pfp_public_id = None
        user.pfp = None
    db.commit()
    db.refresh(user)
    return user