from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from sqlalchemy.exc import IntegrityError
from security import hash_password, password_verify
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    age: int

models.Base.metadata.create_all(bind=engine)

class UserLogin(BaseModel):

    email : str
    password : str

class UserUpdate(BaseModel):
    name : Optional[str] = None
    email : Optional[str] = None
    password : Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(user: UserCreate, db : Session = Depends(get_db)):
    try:

        hash_pwd = hash_password(user.password)

        db_user = models.User(
        username = user.username,
        password = hash_pwd,
        email = user.email,
        age = user.age
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return{"status":"success", "data": db_user}
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code = 400,
            detail = "Email already exists!"
        )

@app.get("/users/")
def get_users(db : Session = Depends(get_db)):
    users = db.query(models.User).all()

    return {
        "status" : "Success",
        "count" : len(users),
        "data" : users
    }

@app.get("/users/{user_id}")
def get_user_id(user_id : int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User Not Found')
    return {
        "status" : "Success",
        "data" : user
    }

@app.delete("/users/{user_id}")
def user_delete(user_id : int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user: raise HTTPException(status_code= 404, detail = "The user does not exist!")

    db.delete(user)
    db.commit()

    return{
        "Status" : "Success",
        "message" : f"User with ID {user_id} record has been deleted."
    }

@app.post("/login/")
def login(user_credentials : UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code = 400, detail = "Invalid credentials")
    if not password_verify(user_credentials.password, user.password):
        raise HTTPException(status_code = 400, detail = "Invalid credentials")

    return {"status":"success", "message":"login successful"}

@app.put("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code= 404, detail="User does not exist")

    update_data = user_update.dict(exclude_unset= True)
    if "password" in update_data:
        update_data['password'] = hash_password(update_data['password'])

    for key, value in update_data:
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return {
        "status" : "Success",
        "message" : "Successfully updated!",
        "user" : db_user
    }

@app.get("/users/search/")
def search_user_email(email : str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found!")

    return {
        "Status" : "Success",
        "user" : user
    }