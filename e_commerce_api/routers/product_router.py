from datetime import datetime
from typing import Annotated, List
from fastapi import Depends, APIRouter, HTTPException, status

from e_commerce_api.database import SessionLocal, get_db
from e_commerce_api.models import Product as product_model, User as user_model, WarehouseItem as warehouse_item_model, Warehouse as warehouse_model, Categories as category_model

from sqlalchemy.orm import Session
from e_commerce_api.routers.user_router import get_current_active_user

from e_commerce_api.schemas.product_schema import ProductRequest, ProductResponse

router_product = APIRouter(
    tags=['Product Endpoints']
)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get all products

@router_product.get('/products', response_model=List[ProductResponse])
def get_products(db: SessionLocal = Depends(get_db), limit: int = 10): # type: ignore
    products= db.query(product_model).order_by(product_model.created_at.desc()).limit(limit).all() # type: ignore
       
    return products

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get all products created by a user

@router_product.get('/products-self', response_model=List[ProductResponse])
def get_products(current_user: Annotated[user_model, Depends(get_current_active_user)], db: SessionLocal = Depends(get_db), limit: int = 10): # type: ignore
    products= db.query(product_model).filter(product_model.owner_id==current_user.id).order_by(product_model.created_at.desc()).limit(limit).all()
       
    return products
    
# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to create a new product

@router_product.post('/products', response_model=ProductResponse,)
def create_product(current_user: Annotated[user_model, Depends(get_current_active_user)], product: ProductRequest, db: SessionLocal = Depends(get_db)): # type: ignore
    user = current_user
    category_exists = db.query(category_model).filter(category_model.category == product.category).first() != None
    
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'User does not exist'})
    
    if user.is_seller == False: # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User in not a seller'})
    
    if  category_exists == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'Category does not exist'})

    warehouse_instance = db.query(warehouse_model).filter(warehouse_model.user_id == user.id).first()
    
    for key, value in product.dict(exclude_unset=True).items():
        if value == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'message': f'Invalid input: {key}: {value}'})
        else:
            pass
    
    actual_db_product = product_model(**product.dict())
    setattr(actual_db_product, 'created_at', datetime.now())
    setattr(actual_db_product, 'last_edited', datetime.now())
    db.add(actual_db_product)
    db.commit()
    db.refresh(actual_db_product)
    warehouse_item = warehouse_item_model(warehouse_id=warehouse_instance.id, product_id=actual_db_product.id)
    db.add(warehouse_item)
    db.commit()
    return actual_db_product

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get a specific product

@router_product.get('/products/{product_id}', response_model=ProductResponse, name="Fetch a particular product")
def get_product(current_user: Annotated[user_model, Depends(get_current_active_user)], product_id: int,db: SessionLocal = Depends(get_db)): # type: ignore
    product_details = db.get(product_model, product_id)
    if product_details.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    if product_details == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'product does not exist'})
    return product_details

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to update a product
@router_product.put('/products/{product_id}', response_model=ProductResponse)
def update_product(current_user: Annotated[user_model, Depends(get_current_active_user)], product_id:int,product: ProductRequest, db: SessionLocal = Depends(get_db)): # type: ignore
    db_product = db.get(product_model,product_id)
    
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    
    category_exists = db.query(category_model).filter(category_model.category == product.category).first() != None
    
    if db_product == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'Product does not exist'})
    
    if  category_exists == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': 'Category does not exist'})
    
    for key, value in product.dict(exclude_unset=True).items():
        if value == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'message': 'Invalid input'})
        setattr(db_product, key,value)
    
    setattr(db_product, 'last_edited',datetime.now())
    db.add(db_product)
    db.commit() 
    db.refresh(db_product)
    
    return db_product



# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to delete a product
@router_product.delete('/products/{product_id}')
def delete_product(current_user: Annotated[user_model, Depends(get_current_active_user)], product_id: int, db:SessionLocal = Depends(get_db)): # type: ignore
    db_product = db.get(product_model, product_id)
    
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    
    db_warehouse_item = db.query(warehouse_item_model).filter(warehouse_item_model.product_id == db_product.id).first()
    db.delete(db_warehouse_item)
    db.delete(db_product)
    db.commit()
    
    raise HTTPException(status_code=status.HTTP_200_OK, detail={'message': 'Product deleted successfully'})    

# ------------------------------------------------------------------------------------------------------------------------------------


