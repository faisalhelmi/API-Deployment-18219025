import json
from fastapi import FastAPI, HTTPException

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#username admin : admin
#password admin : admin
fake_admin_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin 1",
        "email": "admin@studiin.com",
        "hashed_password": "$2b$10$8M2NAGjDyXFAwEiq9FrldOxq6O5PoosdtpjOIlw2vbyFAzCj26/va", 
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

with open("tutor.json", "r") as readfile:
    data = json.load(readfile)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_admin_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_admin_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get('/')
def root():
    return{'Sistar Studiin'}

#lihat semua list tutor semua status
@app.get('/listtutor')
async def read_tutor(current_user: User = Depends(get_current_active_user)):
    return data

#mengakses data seorang tutor
@app.get('/datatutor/{tutorid}')
async def read_tutor(tutor_id: int, current_user: User = Depends(get_current_active_user)):
    
    for list_tutor in data['Data Tutor']:
        if list_tutor['tutorid'] == tutor_id:
            return list_tutor

    raise HTTPException(
        status_code=404, detail=f'Tutor not found'
        )
        
#mengubah nama tutor
@app.put('/datatutor/{tutorid}') 
async def edit_name(tutor_id: int,nama: str, current_user: User = Depends(get_current_active_user)): 

    for list_tutor in data['Data Tutor']:
        if list_tutor['tutorid'] == tutor_id:
            list_tutor['nama']=nama
            read_file.close()
            with open("tutor.json", "w") as write_file: 
                json.dump(data,write_file)
            write_file.close()
            return{'message':'Nama Updated'}

    raise HTTPException(
        status_code=404, detail=f'Tutor not found'
    )

#mengubah email tutor
@app.put('/datatutor/{tutorid}') 
async def edit_email(tutor_id: int,email: str, current_user: User = Depends(get_current_active_user)): 

    for list_tutor in data['Data Tutor']:
        if list_tutor['tutorid'] == tutor_id:
            list_tutor['email']=email
            read_file.close()
            with open("tutor.json", "w") as write_file: 
                json.dump(data,write_file)
            write_file.close()
            return{'message':'Email Updated'}

    raise HTTPException(
        status_code=404, detail=f'Tutor not found'
    )
