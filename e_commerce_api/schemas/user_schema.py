from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None


class UserRegister(BaseModel):
    is_seller: Optional[bool]
    username: Optional[str]
    email: str
    password: str
    
    class Config:
        orm_mode = True
        
class UserLogin(BaseModel):
    username: Optional[str]
    password: str
    email: str
    
    class Config:
        orm_mode = True
    
class UserUpdate(BaseModel):
    email: Optional[str]
    username: Optional[str]
    
    
    class Config:
        orm_mode = True

class PasswordRequest(BaseModel):
    email: str
    old_password: str
    new_password: str
    

class OrderProducts(BaseModel):
    order_product_id:int
    product_id:int
    quantity: int
    price: int
    total_price: int
    
    class Config:
        orm_mode = True
    

# User Response for Getting users
class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    is_seller: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class SellerResponse(UserResponse):
    warehouse_id: int