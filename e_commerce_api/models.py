'''
models.py file is for defining table structures for your DATABASE
This file creates kind of a link between sqlalchemy and python

'''

from datetime import datetime
import enum
from typing import List
from sqlalchemy import DECIMAL, TIMESTAMP, Boolean, Column, Enum, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import relationship

from .database import Base


class Categories(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    category = Column(String, nullable=False, unique=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    
    username = Column(String, unique = True,nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now(), default=datetime.now())
    last_edited = Column(TIMESTAMP(timezone=True),
                       nullable=False, onupdate=func.now(), default=datetime.now()) 
    is_seller = Column(Boolean, default=False)
    
    # Foreign key relations
    warehouse = relationship("Warehouse", back_populates="seller", uselist=False, lazy="joined")
    orders = relationship("Orders", back_populates="user", lazy="joined")
    cart = relationship("Cart", back_populates='user', uselist=False, lazy="joined")
    chats = relationship("Connection", back_populates='user')
    

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, index=True)
    description = Column(String, index=True, nullable=False)
    price = Column(DECIMAL, nullable=False)
    quantity_available = Column(DECIMAL, nullable = True)
    category = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=func.now() )

    # Foreign key relations
    order_products = relationship("OrderItem", back_populates='product')
    cart_items= relationship('CartItem', back_populates='product')
    warehouse_items = relationship("WarehouseItem", back_populates='product')
    
    
    def __str__(self):
        return f"title: {self.title}\ndescription: {self.description}"
    
class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique = True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=datetime.now())
    last_edited = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=datetime.now() )
    
    # Foreign key relations
    user = relationship("User", back_populates="cart", lazy='joined')
    cart_items = relationship("CartItem", back_populates="cart", uselist=True) 
    
    def __str__(self):
        return f"id:{self.id}\nuser_id:{self.user_id}\ncart_items:{self.cart_items}"    
    
    
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    # Foreign key relations
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items", uselist=False)
    
    def __str__(self):
        return f"id:{self.cart_id}\nuser_id:{self.product_id}"   
    
    
class Warehouse(Base):
    __tablename__ = "warehouse"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique = True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=datetime.now())
    last_edited = Column(TIMESTAMP(timezone=True),
                       nullable=False, default=datetime.now() )
    
    # Foreign key relations
    seller = relationship("User", back_populates="warehouse", lazy='joined')
    warehouse_items = relationship("WarehouseItem", back_populates="warehouse") 
    
    def __str__(self):
        return f"id:{self.id}\nuser_id:{self.user_id}"    
    
    
class WarehouseItem(Base):
    __tablename__ = "warehouse_items"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouse.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Foreign key relations
    warehouse = relationship("Warehouse", back_populates="warehouse_items", lazy='joined')
    product = relationship("Product", back_populates="warehouse_items")
    
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    order_date = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now(),)
    
    order_quantity = Column(DECIMAL, nullable = False)
    total_price = Column(DECIMAL, nullable=False)
    
    # Foreign key relations
    order_product = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates='orders')
    

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), index=True, nullable=False)
    quantity = Column(DECIMAL, nullable=False)
    price = Column(DECIMAL, nullable=False)
    total_price = Column(DECIMAL, nullable=False)
    
    # relationship with order
    order = relationship("Orders", back_populates="order_product")
    
    # relationship with Product
    product = relationship("Product", back_populates='order_products')
    
    def __str__(self):
        return f"id:{self.id}\norder_id:{self.order_id}"
    
    
class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    connection_id = Column(Integer, ForeignKey('connections.id'),nullable=False)
    sender_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=func.now())
    description = Column(String)
    image = Column(String)
    
    
    connection = relationship("Connection", back_populates='chats')
    
    
    def __str__(self):
        return f"id:{self.id}\nfrom:{self.from_id}\nto_id:{self.to_id}\n description:{self.description}"

    
class Connection(Base):
    __tablename__ = 'connections'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    receiver_id = Column(Integer,  nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=func.now())
    
    chats = relationship("Chat", back_populates='connection')
    user = relationship("User", back_populates='chats')
    
    def __str__(self):
        return f"id:{self.id}\nuser_id:{self.user_id}\nconnection_id:{self.connection_id}"
    
