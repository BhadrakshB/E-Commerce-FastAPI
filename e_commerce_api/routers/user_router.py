from datetime import datetime, timedelta
from typing import Annotated, List

from e_commerce_api.secret_key import SECRET_KEY
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from e_commerce_api.database import get_db
from e_commerce_api.models import User as user_model, Cart as cart_model, Warehouse as warehouse_model, Product as product_model, WarehouseItem as warehouse_item_model, CartItem as cart_item_model
from e_commerce_api.schemas.user_schema import Token, TokenData, UserResponse, UserRegister, PasswordRequest
import re
from sqlalchemy.orm import Session
from passlib.context import CryptContext

password_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(original_password) -> str:
    return password_context.hash(original_password)

def verify_password(original_password,hashed_password) -> bool:
    return password_context.verify(original_password, hashed_password)

# CREATES ACCESS TOKEN ----------------------------------------------------------

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------------------------------------------------------------------

# GET USER USING PROVIDED TOKEN -----------------------------------------------------------------

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db : Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(user_model).filter(user_model.email == token_data.username).first() 
    if user is None:
        raise credentials_exception
    return user

# -----------------------------------------------------------------------------------------------

async def get_current_active_user(
    current_user: Annotated[user_model, Depends(get_current_user)]
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


router_user = APIRouter(
    tags=['User Endpoints'],
)

router_auth = APIRouter(
    tags=['AUTHENTICATION Endpoints'],
)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to register a new user

@router_user.post("/users/register", response_model=UserResponse, name="Create a new user" )
def create_user(user: UserRegister, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    
    user_details = user_model(**user.dict())
    user_details.__setattr__('password', hashed_password)
    
    db.add(user_details)
   
    db.commit()
    db.refresh(user_details)
    
    if user.is_seller:
        user_warehouse = warehouse_model(user_id=user_details.id)
        db.add(user_warehouse)
    else:
        user_cart = cart_model(user_id=user_details.id)
        db.add(user_cart)
        
    db.commit()
    db.refresh(user_details)       
    access_token = create_access_token(
        data={"sub": user_details.email}
    )
    
    
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to let user login

@router_auth.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session= Depends(get_db)):
    # user = authenticate_user(form_data.username, form_data.password,db)
    is_email = re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', form_data.username)
    user = db.query(user_model).filter(user_model.email == form_data.username).first()if is_email else db.query(user_model).filter(user_model.username == form_data.username).first() 
    print(user)
    if not user:
        user =  False
    if not verify_password(form_data.password, user.password): # type: ignore
        user = False
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, # type: ignore
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to update user data

@router_user.put("/user",response_model=UserResponse, name="Update a user details with a particular id")
def update_user(user: UserRegister, current_user: Annotated[user_model, Depends(get_current_active_user)], db: Session = Depends(get_db), ):
    
    user = current_user
    
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'User does not exist'})
    
    for key, value in user.dict(exclude_unset=True).items():
        setattr(user, key,value)
    
    setattr(user, 'last_edited',datetime.now())
    db.add(user)
    db.commit() 
    db.refresh(user)
    
    return user

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to change user password

@router_user.put("/users/password", name="Changes a users password with a particular id")
def update_user_password(current_user: Annotated[user_model, Depends(get_current_active_user)],user: PasswordRequest, db: Session = Depends(get_db)):
    
    user = current_user    
    
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'User does not exist'})
    
    user_request_dict = user.dict(exclude_unset=True)
    
    if verify_password(user_request_dict['old_password'], user.password):
        setattr(user, 'password',hash_password(user_request_dict['new_password']))
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'Password cannot be changed'})
            
    db.add(user)
    db.commit()
    db.refresh(user)
    
    raise HTTPException(status_code=status.HTTP_200_OK, detail={'message': 'Password successfully changed'})

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get a particular user's details

@router_user.get("/user", response_model=UserResponse, name="Get details of a particular user")
def get_user(current_user: Annotated[user_model, Depends(get_current_active_user)]):
    user_details = current_user
    if user_details == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message':'User does not exist'})
    
    
    return UserResponse(
        id=user_details.id, # type: ignore
        email=user_details.email, # type: ignore
        username=user_details.username, # type: ignore
        is_seller=user_details.is_seller, # type: ignore
        created_at=user_details.created_at # type: ignore
    )

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get all users details

@router_user.get("/users", response_model=List[UserResponse])
def get_all_users(limit: int = 10, db: Session = Depends(get_db)):
    
    users = db.query(user_model).limit(limit).all()
    
    return users
    
# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to delete user account

@router_user.delete("/users/profile")
def delete_user(current_user: Annotated[user_model, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    user = current_user
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message':'User does not exist'})
    
    if user.is_seller: # type: ignore
        user_warehouse = db.query(warehouse_model).filter().first()
        user_warehouse_items = db.query(warehouse_item_model).filter(warehouse_item_model.warehouse_id == user_warehouse.id).all() # type: ignore
        for i in user_warehouse_items:
            db.delete(db.query(product_model).filter(product_model.id == i.product_id).first())
            db.delete(i)
            
        db.delete(user_warehouse)
            
    else:
        user_cart = db.query(cart_model).filter().first()
        user_cart_items = db.query(cart_item_model).filter(cart_item_model.cart_id == user_cart.id).all() # type: ignore
        
        for i in user_cart_items:
            db.delete(i)
        
        db.delete(user_cart)
        
    db.delete(user)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail={'message':'User successfully deleted'})

# ------------------------------------------------------------------------------------------------------------------------------------
    
    