from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from backend.database.db_models import User
from backend.database.database import engine, get_db, SessionLocal
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the path to the .env file explicitly
env_path = Path(__file__).resolve().parent.parent / "database" / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()
JWT_PASSWORD = os.getenv("JWT_PASSWORD", "password")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #this is where we are able to identify where the JWT is in our code 

#Creating password context, way for us to hash our passwords in the future
pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Creating a secret key for our JWT
SECRET_KEY = JWT_PASSWORD
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    username: str
    password: str

#check if they exist in the database, query User table and filter username column where the exists the type username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
#allow user to create new user based on create_user call
def create_user(db:Session, user: UserCreate):
    #user.password accesses the pydantic model field UserCraete
    hashed_password = pass_context.hash(user.password) #hashing the password entered
    db_user = User(username=user.username, hashed_password =hashed_password) #adding new user
    db.add(db_user)
    db.commit()
    return "complete"

