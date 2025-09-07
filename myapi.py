from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "quensdeveloper"
ALGORITHM = "HS256"
TOKEN_EXPIRES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
engine = create_engine("sqlite:///usersapi.db", connect_args={"check_same_thread" : False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class User(Base):
    __tablename__ ="users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(engine)

#Pydantic Model (Dataclasses)
class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Security functions
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_acces_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp" : expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt
        

def verify_token(token: str)->TokenData:
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Couldn't verify credential",
        headers={"WWW-Authenticate" : "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        return TokenData(email=email)
    
    except jwt.PyJWTError:
        raise credentials_exception
    

# db connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependencies
def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exists",
            headers={"WWW-Authenticate" : "Bearer"}
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=404,
            detail="User is not active"
        )
    return current_user


# APP
app = FastAPI(title="Secure Fast API with JWT and SQL - Queens Developer")

# Auth endpoints
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=404,
            detail="User already created"
        )
    hashed_password = get_pwd_hash(user.password)
    db_user = User(
        name = user.name,
        email = user.email,
        role = user.role,
        hashed_pwd = hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException(
            status_code=404,
            detail="Wrong info!"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=404,
            detail="User is not active"
        )
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_acces_token(
        data={"sub":user.email}, expires_delta=access_token_expires
    )

    return {"access_token" : access_token, "token_type" : "bearer"}

# Endpoint - Root
@app.get("/")
def root():
    return {"message" : "Welcome to FastAPI with SQL"}

@app.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/verify-token")
def verify_token_endpoint(current_user: User = Depends(get_current_active_user)):
    return {
        "valid" : True,
        "user" : {
            "id" : current_user.id,
            "name" : current_user.name,
            "email" : current_user.email,
            "role"  : current_user.role
        }
    }

# Get user
@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id:int, current_user: User = Depends(get_current_active_user), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user

# Create user
@app.post("/user/", response_model=UserResponse)
def create_user(user: UserCreate, current_user: User = Depends(get_current_active_user), db:Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="User already exists!")
    
    hashed_password = get_pwd_hash(user.password)
    db_user = User(
        name = user.name,
        email = user.email,
        role = user.role,
        hashed_pwd = hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# Update user
@app.put("/user/{user_id}", response_model=UserResponse)
def update_user(user_id:int, update_user:UserCreate, current_user: User = Depends(get_current_active_user), db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    
    db_user.name = update_user.name,
    db_user.email = update_user.email,
    db_user.role = update_user.role
    
    db.commit()
    db.refresh(db_user)

    return db_user

# Delete user
@app.delete("/user/{user_id}")
def delete_user(user_id:int, current_user: User = Depends(get_current_active_user), db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    
    if db_user.id == current_user.id:
        raise HTTPException(status_code=404, detail="You cant delete yourself!")
    
    db.delete(db_user)
    db.commit()

    return {"message" : "User deleted!"}

# Get all users
@app.get("/users/", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(get_current_active_user), db:Session = Depends(get_db)):
    return db.query(User).all()