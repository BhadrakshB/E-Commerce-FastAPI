# TODO: Complete order routers today

from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from e_commerce_api.database import SessionLocal, get_db
from e_commerce_api.routers.user_router import get_current_active_user

from e_commerce_api.schemas.order_schema import CreateOrder, Order # type: ignore
from e_commerce_api import models

router_order = APIRouter(
    tags = ['Order Endpoints']
)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to create a new order
@router_order.post('/orders')
def create_order(current_user: Annotated[models.User, Depends(get_current_active_user)],  order_details : CreateOrder, db : SessionLocal = Depends(get_db)): # type: ignore
    db_user = current_user

   
    if len(order_details.products) == 0:
        raise HTTPException(status_code=200, detail="No products in order  ")
    
    
    if db_user.is_seller == 1: # type: ignore
        raise HTTPException(status_code=200, detail="Seller cannot place orders")
    else:
        order_instance = models.Orders(user_id = db_user.id, order_date = datetime.now(), order_quantity = 0, total_price = 0)
        db.add(order_instance)
        db.commit()
        db.refresh(order_instance)
        order_quantity = 0
        total_price = 0
        for i in order_details.products:
            if i.quantity < 1:
                raise HTTPException(status_code=404, detail="Invalid quantity of products")
            
            else:
                db_product = db.query(models.Product).filter(models.Product.id == i.product_id).first()
                if db_product != None:
                    if db_product.quantity_available < i.quantity:
                        return HTTPException(status_code=400, detail="Not enough products available")
                    if db_product.quantity_available == 0:
                        raise HTTPException(status_code=400, detail="Product out of stock")
                    else:
                        try:
                            order_item_instance = models.OrderItem(product_id = i.product_id, price = db_product.price,quantity = i.quantity, total_price = db_product.price * i.quantity, order_id = order_instance.id)
                            order_quantity += i.quantity
                            total_price += db_product.price * i.quantity
                            db.add(order_item_instance)
                            db_product.quantity_available -= i.quantity
                            db.commit()
                            db.refresh(db_product)
                        except Exception as e:
                            db.delete(order_instance)
                            db.commit()
                            raise HTTPException(status_code=400, detail=f"{e}")
                            
                else:
                    db.delete(order_instance)
                    db.commit()
                    raise HTTPException(status_code=404, detail="Invalid Product ID")
                            
    order_instance.order_quantity = order_quantity # type: ignore
    order_instance.total_price = total_price # type: ignore
    if len(order_details.products) > 1:
        db.delete(db.query(models.CartItem).filter(models.CartItem.cart_id == db_user.cart.id).all())
    db.commit()
    db.refresh(order_instance)
    
    raise HTTPException(status_code=200, detail="Order Placed Successfully")
    
    pass

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get all orders
@router_order.get('/order', response_model=List[Order])
def get_all_orders(db : SessionLocal = Depends(get_db)): # type: ignore
    return list(map(lambda i : Order(id=i.id, user_id=i.user_id, order_date=i.order_date, total_quantity=i.order_quantity, total_price=i.total_price), db.query(models.Orders).filter().all()))# type: ignore
    

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get a specific order
@router_order.get('/orders/{order_id}', response_model=Order)
def get_order(current_user: Annotated[models.User, Depends(get_current_active_user)],order_id: int, db : SessionLocal = Depends(get_db)):  # type: ignore
    order_details = db.query(models.Orders).filter(models.Orders.id == order_id).first()
    
    if order_details.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    
    return Order(id=order_details.id, user_id=order_details.user_id, order_date=order_details.order_date, total_quantity=order_details.order_quantity, total_price=order_details.total_price)

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to get a specific order

@router_order.get('/order-self', response_model=List[Order])
def get_all_orders(current_user: Annotated[models.User, Depends(get_current_active_user)], db : SessionLocal = Depends(get_db)): # type: ignore
    return list(map(lambda i : Order(id=i.id, user_id=i.user_id, order_date=i.order_date, total_quantity=i.order_quantity, total_price=i.total_price), db.query(models.Orders).filter(models.Orders.user_id == current_user.id).all()))# type: ignore

# ------------------------------------------------------------------------------------------------------------------------------------

# TODO: API Endpoint to update a specific order
# @router_order.put('/orders/{order_id}')
# def update_order(order_id: int): # type: ignore
#     pass

# ------------------------------------------------------------------------------------------------------------------------------------

# API Endpoint to cancel a specific order
@router_order.delete('/orders/{order_id}')
def cancel_order(current_user: Annotated[models.User, Depends(get_current_active_user)],order_id: int, db : SessionLocal = Depends(get_db)): # type: ignore
    order_details = db.query(models.Orders).filter(models.Orders.id == order_id).first()
    
    if order_details.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'message': 'User not authorized'})
    
    db.delete(order_details)
    db.commit()
    
    raise HTTPException(status_code=200, detail="Order Cancelled Successfully")



