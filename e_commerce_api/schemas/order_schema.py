from datetime import datetime
from pydantic import BaseModel
from typing import List

    
class OrderProduct(BaseModel):
    product_id: int
    quantity: int
    

class CreateOrder(BaseModel):
    products: List[OrderProduct]
    

class Order(BaseModel):
    id : int
    user_id : int
    order_date : datetime
    total_quantity : int
    total_price : float
    
    class config:
        orm_mode = True
    