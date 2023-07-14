from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

        
class ProductRequest(BaseModel):
    title: str
    description: str
    price: float
    quantity_available: float
    category: str
    owner_id:int
    
    class Config:
        orm_mode = True
        
class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    created_at: datetime 
    
    class Config:
        orm_mode = True
        
class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    quantity_available: float
    category: str
    owner_id: int
    created_at: datetime
    last_edited: datetime
    
    class Config:
        orm_mode = True

        
class Warehouse(BaseModel):
    # total_value: int
    products: List[ProductResponse]
    
    class Config:
        orm_mode = True


class SingleOrderRequest(BaseModel):
    
    order_user: int
    order_quantity: float
    total_price: float
    product_ids: List[int]
    
    
    
    class Config:
        orm_mode = True


class OrderRequest(BaseModel):
    user_id: int
    amount_paid:int
    orders: List[SingleOrderRequest]
    
    class Config:
        orm_mode = True

class ItemRequest(BaseModel):
    title: str
    description: str
    price: float
    quantity_available: int
    category: str
    
    
    class Config:
        orm_mode = True
        

