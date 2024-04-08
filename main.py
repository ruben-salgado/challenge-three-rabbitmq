from fastapi import FastAPI, BackgroundTasks
from typing import List
from celery import Celery
from models.Carrito import Carrito
from models.Producto import Producto

import json

app = FastAPI()

celery = Celery('tasks', broker='amqp://admin:admin@localhost:5672//',backend='rpc://')

@app.post("/tienda")
async def send_message_sale(carrito: Carrito):
    result = celery.send_task("tasks.send_tienda", args=[carrito.dict()], queue="tienda")
    return {"status": "Message sent to Celery for processing for sale", "task_id": result.id}
