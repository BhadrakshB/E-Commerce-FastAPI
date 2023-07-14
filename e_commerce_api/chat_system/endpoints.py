import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from e_commerce_api import models

from sqlalchemy import or_, and_

from e_commerce_api.database import SessionLocal, get_db

chat = APIRouter(
    tags = ['Chat Endpoint']
)

@chat.get("/")
def get_connection(sender_id: int, receiver_id: int, db : SessionLocal = Depends(get_db)): # type: ignore
    try:
        return db.query(models.Connection).filter(or_(
            and_(models.Connection.sender_id == sender_id ,models.Connection.receiver_id == receiver_id),
                and_(models.Connection.sender_id == receiver_id, models.Connection.receiver_id == sender_id)
            )).first().id
    except:
        connection = models.Connection(sender_id = sender_id, receiver_id = receiver_id)
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection.id        
    

@chat.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db : SessionLocal = Depends(get_db)): # type: ignore
    try:
        messages = db.query(models.Chat).filter(models.Chat.connection_id == client_id).order_by(models.Chat.created_at ).limit(10).all()
        
        print(messages[0])
        
        await websocket.accept()
        
        # messages = messages[::-1]
        
        print("Runnign loop")
        
        for message in messages:
            print(f"message from loop: {message}")
            # await websocket.send_json(
            #         json.dumps(message.__dict__)
            #     ) # type: ignore
            
        while True:
            
            data = await websocket.receive_json()
            
            print(data)
            
            try:
                
                db.add(models.Chat(description = data['description'], connection_id = client_id, sender_id = data['sender_id']))
                db.commit()
                await websocket.send_json(jsonable_encoder(data))
            except Exception as e:
                print(f"1 Exception: {e}")
    except Exception as e:
        print(f"2 Exception: {e}")