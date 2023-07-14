from typing import List, Optional
from pydantic import BaseModel


class AddProductRequest(BaseModel):
    cart_id : int
    product_id : int
    quantity : Optional[int]

class CartProductRequest(BaseModel):
    product_id: int
    quantity: int
    title: str
    price: float
    description: str

class CartProductResponse(BaseModel):
    id: int
    title : str
    description : str
    price : float
    quantity_available : int
    category : str
       
    class config:
        orm_mode = True

class CartResponse(BaseModel):
    id : int
    user_id : int
    products : List[CartProductResponse] = []
    
    class config:
        orm_mode = True