from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime,timedelta
from jose import jwt
from app.dependencies import SessionDep,Session
from app.models.users import User
from fastapi import APIRouter,Depends
from sqlalchemy import or_
from fastapi.exceptions import HTTPException
from fastapi import status
from app.schemas.users_schemas import UserCreate,UserDisplay
from app.dependencies import SessionDep
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
import dotenv
import os

dotenv.load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRES_MINUTES')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login/')
oauth2_scheme_silent = OAuth2PasswordBearer(tokenUrl='auth/login/',auto_error=False)
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')


def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES))
    to_encode.update(
        {'exp':expire}
    )
    return jwt.encode(data,key=SECRET_KEY,algorithm=ALGORITHM)

def verify_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        return payload
    except:
        return None
    

def authenticate(email:str,password:str,db:SessionDep):
    #first we query the user
    user = db.query(User).filter(User.email==email).first()
    if not user:
        return False
    if not pwd_context.verify(password,user.password):
        return False
    return user   #the user is legitimate to login




auth_router = APIRouter(prefix='/auth',tags=['auth'])


@auth_router.post('/register/',response_model=UserDisplay,status_code=status.HTTP_201_CREATED)
async def register(user:UserCreate,db:SessionDep):
    #check if the user already exists
    user_db = db.query(User).filter(   
        or_(
            User.email == user.email,
            User.username == user.username,
        )
    ).first()
    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="user with this username/email is already registered")
    
    #we create a new user
    user_data = user.model_dump()
    user_data["password"] = pwd_context.hash(user.password)   #hash the password
    user_db = User(**user_data)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db



@auth_router.post('/login/')
async def login(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],db:SessionDep):
    #authenticate the user
    user = authenticate(form_data.username,form_data.password,db)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail='we could not authenticate you, verify your username or password'
        )

    #generate token
    data = {
        'sub' : user.email,   #we use the email for the token
    }
    token = create_token(data)
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }


    
def current_user(token:Annotated[str,oauth2_scheme],db:Session):
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload['sub']  #retrieve the email from the decoded token

    user = db.query(User).filter(User.email==email).first()  #search for the user with the email
    return user



@auth_router.get('/current_user/',response_model=UserDisplay)
async def get_current_user(db:SessionDep,token:Annotated[str|None,Depends(oauth2_scheme)]=None):
    return  current_user(token,db)
    
from typing import Optional

def current_user2(
    token: Annotated[Optional[str], Depends(oauth2_scheme_silent)], 
    db: SessionDep
) -> Optional[User]:
    if not token:   # No token provided
        print("zbu")
        return None
    
    print("Got token:", token)  

    payload = verify_token(token)
    if not payload:
        return None  # instead of raising

    email = payload.get("sub")
    if not email:
        return None

    user = db.query(User).filter(User.email == email).first()
    return user


@auth_router.get("/currentuser/", response_model=UserDisplay)
async def read_current_user(
    user: Annotated[User, Depends(current_user2)]
):
    return user


@auth_router.post('/pass/')
def rfeerr(pswrd:str):
    print(pwd_context.hash(pswrd))
