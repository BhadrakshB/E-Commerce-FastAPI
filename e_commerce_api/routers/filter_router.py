# This file contains the endpoints for searching and filtering products.

# Filter products by price range: GET /products?min_price={min_price}&max_price={max_price}
# Sort products by various criteria: GET /products?sort={criteria}

from enum import Enum
from typing import List
from fastapi import APIRouter, Depends
from e_commerce_api import models
from sqlalchemy import or_
from e_commerce_api.database import SessionLocal, get_db
from e_commerce_api.schemas.filter_schema import SearchProductResponse


router_search_filter = APIRouter(
    tags = ['Search and Filter Endpoints']
)

class SortCriteria(Enum):
    title = 'title'
    price_asc = "price_asc"
    price_dsc = "price_dsc"
    latest = "latest"

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint for searching products by category id

@router_search_filter.get('/products/', response_model=List[SearchProductResponse])
def get_products_search(keyword:str | None = None, category_id: int | None = None, sort_by : SortCriteria | None = None,db : SessionLocal = Depends(get_db)): # type: ignore
    
    db_products = []
    
    if keyword == None and category_id == None:
        db_products = db.query(models.Product).all()
    elif keyword == None and category_id != None:
        db_category_name = db.query(models.Categories).filter(models.Categories.id == category_id).first().category # type: ignore
        db_products = db.query(models.Product).filter(models.Product.category == db_category_name).all() # type: ignore
    elif keyword != None and category_id == None:
        db_products = db.query(models.Product).filter(or_(models.Product.title.contains(keyword), models.Product.description.contains(keyword))).all() # type: ignore
    else:
        db_category_name = db.query(models.Categories).filter(models.Categories.id == category_id,).first().category
        db_products = db.query(models.Product).filter(or_(models.Product.title.contains(keyword), models.Product.description.contains(keyword)), models.Product.category == db_category_name).all() # type: ignore
    
    if sort_by == SortCriteria.title:
        db_products = sorted(db_products, key=lambda x: x.title)
    elif sort_by == SortCriteria.price_asc:
        db_products = sorted(db_products, key=lambda x: x.price,)
    elif sort_by == SortCriteria.price_dsc:
        db_products = sorted(db_products, key=lambda x: x.price, reverse=True)
    elif sort_by == SortCriteria.latest:
        db_products = sorted(db_products, key=lambda x: x.id)
        
    
    products = [SearchProductResponse.from_orm(i) for i in db_products]
    return products



