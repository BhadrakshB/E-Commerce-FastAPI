
from pydantic import BaseModel



class SearchProductResponse(BaseModel):
    id : int
    title : str
    description : str
    owner_id: int
    price : float
    quantity_available : int
    category : str
    
    class Config:
        orm_mode = True