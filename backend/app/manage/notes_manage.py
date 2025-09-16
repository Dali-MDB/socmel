from fastapi.routing import APIRouter
from app.dependencies import SessionDep
from app.models.notes import Note
from app.models.users import User
from typing import Annotated
from fastapi import Depends
from app.authentication import oauth2_scheme,current_user
from .users_manage import fetch_user
from datetime import datetime,timedelta
from fastapi.responses import JSONResponse

notes_router = APIRouter(prefix='/note',tags=['notes'])


@notes_router.get('/{user_id}')
async def get_note(user_id:int,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = fetch_user(user_id,db)
    print(user.note)

    note = user.note if (user.note) and (user.note.created_at + timedelta(hours=24,minutes=0))> datetime.now() else None
    return {
        "exists" : True if note else False,
        "note": note.content if note else ""
        }





@notes_router.post('/')
async def create_note(new_note:str,db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    note : Note = None
    if user.note:
        note = user.note
        note.content = new_note
        note.created_at = datetime.now()
        
    else:   #we create one
        note = Note(
            user_id = user.id,
            content= new_note,
        )
        db.add(note)
    
    db.commit()
    db.refresh(note)
    print(note)
    print(user.note)
    return JSONResponse({
        'message' : 'the note has been added successfully',
        'note':note.content
    })


@notes_router.delete('/')
async def delete_note(db:SessionDep,token:Annotated[str,Depends(oauth2_scheme)]):
    user = current_user(token,db)
    if user.note:
        note = user.note
        db.delete(note)
        db.commit()

    return JSONResponse({
        "message":"the note has been deleted successfully"
    })