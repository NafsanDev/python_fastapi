# without sql
from fastapi import FastAPI, HTTPException, status, Path
from typing import Optional
from pydantic import BaseModel


app = FastAPI()

users = {
    1: {
        "name" : "Queens",
        "email" : "queens@example.com",
        "age" : "65",
        "webiste" : "queensdev.com",
        "role" : "Developer",
        "photo" : "url"
    },
    2: {
        "name" : "Nafsan",
        "email" : "nafsan@example.com",
        "age" : "25",
        "webiste" : "nafsan.com",
        "role" : "Admin",
        "photo" : "url"
    },
    3: {
        "name" : "Kings",
        "email" : "kings@example.com",
        "age" : "24",
        "webiste" : "kingsconsumers.com",
        "role" : "Subscriber",
        "photo" : "url"
    }
}

#Base pydantic models
class User(BaseModel):
    name:str
    email:str
    website:str
    age:int
    role:str
    photo:str


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    photo: Optional[str] = None

# endpoint (url)
@app.get('/')
def root():
    return {"message" : "Welcome to FastAPI"}

# get users
# example.com/user/1
@app.get("/user/{user_id}")
def get_user(user_id:int = Path(..., description="The Id you want", gt=0, lt=100)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

# create user
# example.com/user/1
@app.post("/user/{user_id}", status_code=status.HTTP_201_CREATED)
def create_user(user_id:int, user:User):
    if user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user_id] = user.model_dump()
    return user

# update user
# example.com/user/1
@app.put("/user/{user_id}")
def update_user(user_id:int, user:UpdateUser):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    current_user = users[user_id]
    if user.name is not None:
        current_user["name"] = user.name
    if user.email is not None:
        current_user["email"] = user.email
    if user.website is not None:
        current_user["website"] = user.website
    if user.age is not None:
        current_user["age"] = user.age
    if user.role is not None:
        current_user["role"] = user.role
    if user.photo is not None:
        current_user["photo"] = user.photo
    return current_user

# delete user
# example.com/user/41
@app.delete("/user/{user_id}")
def delete_user(user_id:int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = users.pop(user_id)
    return {"message" : "User deleted successfully", "deleted_user" : deleted_user}

# search user
# example.com/user/search?queens
@app.get("/user/search/")
def search_user_by_name(name : Optional[str] = None):
    if not name:
        return {"message" : "Name is required"}
    for user in users.values():
        if user["name"].lower() == name.lower():
            return user
                
    raise HTTPException(status_code=404, detail="User not found")
