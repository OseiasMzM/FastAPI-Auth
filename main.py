from typing import Optional
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.models.modelUser import User

import hashlib


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "1659c624ea25e8a1057ba801c8eba094",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "2361ca28dc49f9979ed3dfe89466a592",
        "disabled": False,
    },
}

app = FastAPI()

def fake_hash_password(password: str):
    salt = "5gz"
    dataBase_password = password+salt
    hashed = hashlib.md5(dataBase_password.encode())
    # print(hashed.hexdigest())
    password = hashed.hexdigest()
    # print(password)
    return password
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user



async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users")
async def all_users():
    return fake_users_db


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8000, 
                log_level="info",
                reload=True)