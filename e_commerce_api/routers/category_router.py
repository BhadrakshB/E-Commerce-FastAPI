from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

import sqlalchemy
from e_commerce_api import models
from e_commerce_api.database import SessionLocal, get_db
from e_commerce_api.schemas import category_schema

router_category = APIRouter(
    tags = ['Category Endpoints']
)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get all categories
@router_category.get('/categories')
def get_categories(db : SessionLocal = Depends(get_db)): # type: ignore
    categories = db.query(models.Categories).all()
    return categories

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get a specific category
@router_category.get('/categories/{category_id}')
def get_category(category_id: int, db : SessionLocal = Depends(get_db)): # type: ignore
    categories = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    return categories

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to create a category
@router_category.post('/categories')
def post_category(category: category_schema.CategoryRequest, db : SessionLocal = Depends(get_db)): # type: ignore
    try:
        categories = models.Categories(category=category.name)
        db.add(categories)
        db.commit()
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Category created")
    except sqlalchemy.exc.IntegrityError as error: # type: ignore
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"error: {e}")
    
# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to update a category
@router_category.put('/categories/{category_id}')
def post_category(category_id: int, details : category_schema.CategoryRequest, db : SessionLocal = Depends(get_db)): # type: ignore
    try:
        category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
        category.category = details.name
        db.commit()
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Category updated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"error: {e}")
    
# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to delete a category
@router_category.delete('/categories/{category_id}')
def post_category(category_id: int, db : SessionLocal = Depends(get_db)): # type: ignore
    try:
        category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
        db.delete(category) 
        db.commit()
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Category deleted")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"error: {e}")
    
# ------------------------------------------------------------------------------------------------------------------------------------
