import random
import string
from fastapi import APIRouter,Depends,Body
from app.schemas.security_schemas import ChangeEmail,ChangePassword
from app.dependencies import SessionDep
from app.authentication import oauth2_scheme,pwd_context
from typing import Annotated
from app.models.users import User
from app.models.security import EmailVerificationCode,verification_code_purpose
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime,timedelta
from app.authentication import current_user

sec_auth = APIRouter(prefix='/security',tags=['security'])
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@sec_auth.post('/request_verification_code/')
async def request_verification_code(email:Annotated[str,Body(...)],purpose:Annotated[verification_code_purpose,Body(...)],db:SessionDep):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404,detail='this user does not exist')
    
    ver_code = db.query(EmailVerificationCode).filter(EmailVerificationCode.email == email).first()
    if ver_code:  #delete it
        db.delete(ver_code)
        db.commit()
    
    code = generate_random_code()
    ver_code = EmailVerificationCode(
        email = email,
        purpose = purpose,
        code = code,
        expires_at = datetime.now() + timedelta(minutes=10)
    )
    db.add(ver_code)
    db.commit()
    #send an email here
    return {'detail':'the verification code has been sent successfully, check your email'}

    


@sec_auth.post('/change_email/',status_code=status.HTTP_200_OK)
async def change_email(change_email_schema:ChangeEmail,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    #verify visiting user
    if user.email != change_email_schema.old_email:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'you are not allowed to change this email with this account')
    code = change_email_schema.key
    #we search for the token
    verf_code = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.code == code,
        EmailVerificationCode.email == change_email_schema.old_email,
    ).first()

    if not verf_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail='incorrect code, try again')
    #in case it has already been used or expired
    if verf_code.expires_at < datetime.now():
        db.delete(verf_code)
        db.commit()
        raise HTTPException(status.HTTP_410_GONE,detail='the code you entered is no longer valid, generate a new one')
    

    #at this level the verification code is valid, so we proceed with email reset
    user.email = change_email_schema.new_email
    db.delete(verf_code)  #delete the reset key (can only be used once)
    db.commit()
    return {'detail':'the email has been changed successfully'}




@sec_auth.post('/change_password/')
async def change_password(change_password_schema:ChangePassword,token:Annotated[str,Depends(oauth2_scheme)],db:SessionDep):
    user = current_user(token,db)
    #verify visiting user
    if user.email != change_password_schema.email:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'you are not allowed to change this email with this account')
    code = change_password_schema.key
    #we search for the token
    verf_code = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.code == code,
        EmailVerificationCode.email == change_password_schema.email,
    ).first()

    if not verf_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail='incorrect code, try again')
    #in case it has already been used or expired
    if  verf_code.expires_at < datetime.now():
        db.delete(verf_code)
        db.commit()
        raise HTTPException(status.HTTP_410_GONE,detail='the code you entered is no longer valid, generate a new one')
    

    #check matching passwords
    if change_password_schema.new_password != change_password_schema.new_password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password and confirmation do not match")
    #at this level the verification code is valid, so we proceed with password reset
    user.password = pwd_context.hash(change_password_schema.new_password)
    db.delete(verf_code)   #delete the reset key (can only be used once)
    db.commit()
    return {'detail':'the password has been changed successfully'}




@sec_auth.post('/reset_password/')
async def reset_password(change_password_schema:ChangePassword,db:SessionDep):
    user = db.query(User).filter(User.email==change_password_schema.email).first()
    if not user:
        raise HTTPException(404,'this account does not exist')
    code = change_password_schema.key
    #we search for the token
    verf_code = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.code == code,
        EmailVerificationCode.email == change_password_schema.email,
    ).first()

    if not verf_code:
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail='incorrect code, try again')
    #in case it has already been used or expired
    if verf_code.expires_at < datetime.now():
        db.delete(verf_code)
        db.commit()
        raise HTTPException(status.HTTP_410_GONE,detail='the code you entered is no longer valid, generate a new one')
    

    #check matching passwords
    if change_password_schema.new_password != change_password_schema.new_password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password and confirmation do not match")
    #at this level the verification code is valid, so we proceed with password reset
    user.password = pwd_context.hash(change_password_schema.new_password)
    db.delete(verf_code)   #delete the reset key (can only be used once)
    db.commit()
    return {'detail':'the password has been changed successfully'}


