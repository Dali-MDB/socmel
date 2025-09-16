from fastapi import Request
from app.authentication import SECRET_KEY,ALGORITHM
from jose import jwt
from app.database import SessionLocal
from app.models.users import User

async def get_auth_details(request: Request, call_next):
    request.state.cur_user = None
    request.state.is_authenticated = False

    auth_header = request.headers.get("authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
        
            token = parts[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    
                # Example: attach user info from payload
                email = payload.get("sub")
                db = SessionLocal()
                user = db.query(User).filter(User.email==email).first()
                print(user)
                if user:
                    request.state.is_authenticated = True
                    request.state.cur_user = user.id
            except Exception:
                # invalid/expired → do nothing
                pass

    response = await call_next(request)
    return response
