from datetime import datetime, timedelta
from http.client import HTTPResponse
from fastapi import  FastAPI, WebSocket
from fastapi.testclient import TestClient
from fastapi.responses import HTMLResponse
import uvicorn
from e_commerce_api import models, database
from e_commerce_api.routers import product_router, user_router, cart_router, order_router,category_router, filter_router
from e_commerce_api.chat_system.endpoints import chat

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(router = chat)

app.include_router(router=product_router.router_product)
app.include_router(router=user_router.router_user)
app.include_router(router=user_router.router_auth)
app.include_router(router=cart_router.router_cart)
# app.include_router(router = files_router)
app.include_router(router = order_router.router_order)
app.include_router(router = category_router.router_category)
app.include_router(router = filter_router.router_search_filter)

def create_mock_data():
    
    db = database.SessionLocal()
    
    values = ['fruits', 'vegetables', 'dairy', 'meat', 'seafood', 'beverages', 'snacks', 'canned', 'frozen', 'baking', 'household', 'personal care', 'other']
    
    for i in values: # type: ignore
        category_i = models.Categories(category=i)
        db.add(category_i)
        db.commit()
    
    user_1 = models.User(username = 'flashbad',email = 'bhadrakshb@gmail.com',password = user_router.hash_password('testing123'), is_seller = 1)
    user_2 = models.User(username = 'divyanshisnotjacked',email = 'divyanshisnotjacked@gmail.com',password = user_router.hash_password('testing123'))
    
    db.add_all([user_1, user_2])
    db.commit()
    db.refresh(user_1)
    db.refresh(user_2)
    
    cart_2 = models.Cart(user_id = user_2.id)
    warehouse_1 = models.Warehouse(user_id=user_1.id)
   
    db.add_all([cart_2, warehouse_1])
    db.commit()
    db.refresh(warehouse_1)
    
    product_1 = models.Product(title='Apples', description='Juicy Apples',price=10,quantity_available=1000,category = 'fruits',owner_id = 1)
    product_2 = models.Product(title='Oranges', description='Sweet Oranges',price=50,quantity_available=5000,category = 'fruits',owner_id = 1)
    
    db.add_all([product_1, product_2])
    db.commit()    
    db.refresh(product_1)
    db.refresh(product_2)
  
    warehouse_item = models.WarehouseItem(product_id = product_1.id, warehouse_id = warehouse_1.id)
    db.add(warehouse_item)
    warehouse_item = models.WarehouseItem(product_id = product_2.id, warehouse_id = warehouse_1.id)
    db.add(warehouse_item)
    
    db.commit()
    db.close()
    print('stored to db')
    pass

create_mock_data() 

def add_auth_details():
    access_token = '1000.8282f77a2a53f739f5171522f0eb087a.0ed4351b3f2470f0cf373fc0456a1758'
    refresh_token = '1000.2fffc06fc3fb13457bd251b1e0a6e333.582c454591fe1bc0f1a2a1c39a60a1a9'
    expires_at = datetime.utcnow() + timedelta(seconds=3600)
    
    db = database.SessionLocal()
    db.query(models.ZohoAuth).delete()
    db.add(models.ZohoAuth(access_token = access_token, refresh_token = refresh_token, expires_at = expires_at))

    db.commit()

# add_auth_details()

@app.get('/')
def starting():
    return {'detail': 'Welcome to THE CROPCHAIN Project'}

    