'''Add a product to the cart: POST /cart
Get user's cart: GET /cart
Update cart: PUT /cart
Remove a product from the cart: DELETE /cart/{product_id}'''

from datetime import datetime
from typing import Annotated, List
from fastapi import Depends, APIRouter, HTTPException, status
import pydantic
import sqlalchemy

from e_commerce_api.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from e_commerce_api.models import Product as product_model, Cart as cart_model, CartItem as cart_item_model, User as user_model
from e_commerce_api.routers.user_router import get_current_active_user
from e_commerce_api.schemas.cart_schema import AddProductRequest, CartProductResponse, CartResponse


router_cart = APIRouter(
    tags=['Cart Endpoints']
)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to add a product to cart

@router_cart.post('/cart')
def add_product_to_cart(current_user: Annotated[user_model, Depends(get_current_active_user)], details: AddProductRequest, db: SessionLocal = Depends(get_db)):  # type: ignore
    
    try:
        db_cart = db.query(cart_model).filter(cart_model.id == details.cart_id).first()
        
        if db_cart.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    
        if (details.quantity < 0): # type: ignore
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'Quantity mentioned is less than zero'})
      
        
        db.query(product_model).filter(product_model.id == details.product_id).first()
        cart_item = cart_item_model(cart_id = db_cart.id, product_id= details.product_id, quantity= details.quantity if details.quantity != None else 1,)
        db.add(cart_item)
        db.commit()
        db.refresh(db_cart)     
    
        raise HTTPException(status_code=status.HTTP_200_OK, detail={'message': f'Successfully added products with product id: {details.product_id}'})
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'{e}'})

    
   

# ------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to read a cart

@router_cart.get('/cart/{cart_id}', response_model=CartResponse)
def read_cart(current_user: Annotated[user_model, Depends(get_current_active_user)], cart_id: int, db: SessionLocal = Depends(get_db)): # type: ignore
    try:
        user_cart = db.query(cart_model).filter(cart_model.id == cart_id).first()
        
        if user_cart.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
        
        product = []
        for i in user_cart.cart_items:
            product.append(CartProductResponse(id=i.product.id, title=i.product.title,description=i.product.description, price=i.product.price, quantity_available=i.quantity,  category=i.product.category))
        
        print(product)

        return CartResponse(id = user_cart.id, 
                            user_id = user_cart.user_id, 
                            products=product
                            )
           
        
    except pydantic.error_wrappers.ValidationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={'message': f'Could not map database field to Response attributes (ORM error)'})
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'Cart with id {cart_id} does not exist'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'{e}'})        


# ------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to update a cart 

@router_cart.put('/cart')
def modify_product_in_cart(current_user: Annotated[user_model, Depends(get_current_active_user)], details: AddProductRequest, db: SessionLocal = Depends(get_db)): # type: ignore
    try:
        db_cart = db.query(cart_model).filter(cart_model.id == details.cart_id).first()
        
        if db_cart.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
        
        product_exists_instance = db.query(cart_item_model).filter(cart_item_model.cart_id == db_cart.id, cart_item_model.product_id == details.product_id).first()
        product_instance = db.query(product_model).filter(product_model.id == details.product_id).first()
        
        if product_instance.quantity_available < product_exists_instance.quantity + details.quantity:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'Quantity mentioned is greater than quantity available'})
        else:   
            product_exists_instance.quantity += details.quantity if details.quantity != None else 1
            db_cart.last_edited = datetime.now()
            db.commit()
            db.refresh(db_cart) 
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'{e}'})

    pass



# ------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to delete a product from cart

@router_cart.delete('/cart/{cart_id}')
def delete_product_from_cart(current_user: Annotated[user_model, Depends(get_current_active_user)],cart_id:int, product_id:int, db: SessionLocal = Depends(get_db)): # type: ignore
    try:
        product_cart_instance = db.query(cart_item_model).filter(cart_item_model.cart_id == cart_id , cart_item_model.product_id == product_id).first()
        cart_instance = db.query(cart_model).filter(cart_model.id == cart_id).first().last_edited = datetime.now()
        
        if cart_instance.user_id != current_user.id: # type: ignore
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
        
        print(product_cart_instance)
        db.delete(product_cart_instance)
        db.commit()
        db.refresh()
        return {'message': f'Successfully deleted product with id {product_id} from cart with id {cart_id}'}
    except sqlalchemy.orm.exc.UnmappedInstanceError: # type: ignore
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'Cart with id {cart_id} does not exist'})
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'message': f'{e}'})
    pass



# ------------------------------------------------------------------------------------------------------------------------------------