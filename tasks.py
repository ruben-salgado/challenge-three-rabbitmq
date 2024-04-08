from typing import Dict, List
from celery import Celery
from models.Producto import Producto
from models.Carrito import Carrito
from models.Venta import Venta
import redis
import json
celery = Celery('tasks', broker='amqp://admin:admin@localhost:5672/',backend='rpc://')

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@celery.task
def send_tienda(data: Dict):
    carrito = Carrito(**data)
    products_seleccionados = []
    subtotal = 0.0
    
    for producto in carrito.productos:
        product = Producto(name=producto.name, stock=producto.stock, price=producto.price)

        if product.stock > 0:
            products_seleccionados.append(product)
            subtotal += product.stock
        else:
            print("El producto %s no tiene stock para hacer la venta " % (product.name))

    venta = Venta(numero = carrito.numero ,productos = products_seleccionados, subtotal=subtotal, iva=0.15, total=( subtotal * 0.15) + subtotal )
    result = celery.send_task("tasks.send_compra", args=[venta.dict()], queue="compra")
    print("El id del resultado de envio a la cola de ventas es => %s"%(result.id))

@celery.task
def send_compra(data: Dict):
    venta = Venta(numero=data["numero"], productos=data["productos"], subtotal=data["subtotal"], iva=data["iva"], total=data["total"])
    print(f"La venta {venta.numero} se genero correctamente")
    reporte={"numero": venta.numero, "mensaje":"Su venta se genero correctamente"}
    result = celery.send_task("tasks.send_reporte", args=[reporte], queue="reportes")

@celery.task
def send_reporte(data: Dict):
    mensaje=data["mensaje"]
    print(mensaje)
    redis_client.set(data['numero'], mensaje)
    