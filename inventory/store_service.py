import pika
import json
import time
import threading

class StoreService:
    def __init__(self, host='localhost'):
        self.host = host
        self.queue_name = 'inventory_updates'
        self.inventory = {}
        self.connection_established = False
        self.connection = None
        self.channel = None

    def connect(self):
        while not self.connection_established:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name)
                self.channel.basic_consume(queue=self.queue_name,
                                           auto_ack=True,
                                           on_message_callback=self.process_inventory_update)
                print("Conexión establecida. Esperando actualizaciones de inventario...")
                self.connection_established = True
                self.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                print("No se pudo conectar al servicio de inventario. Reintentando en 5 segundos...")
                time.sleep(5)

    def start_consuming(self):
        try:
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error al iniciar el consumo: {e}")
            self.connection_established = False

    def process_inventory_update(self, ch, method, properties, body):
        update = json.loads(body)
        product_id = update['product_id']
        quantity = update['quantity']
        self.inventory[product_id] = quantity
        print(f"Inventario actualizado: Producto {product_id}, Nueva cantidad {quantity}")

    def check_inventory(self, product_id, quantity_requested):
        if not self.connection_established:
            return "NO_CONNECTION"
        
        if quantity_requested <= 0:
            return "INVALID_QUANTITY"
        
        if product_id not in self.inventory:
            return "PRODUCT_NOT_FOUND"
        
        available = self.inventory[product_id]
        if available >= quantity_requested:
            return "AVAILABLE"
        else:
            return "INSUFFICIENT_QUANTITY"

    def run(self):
        threading.Thread(target=self.connect, daemon=True).start()

        while not self.connection_established:
            print("Esperando conexión con el servicio de inventario...")
            time.sleep(2)

        while True:
            try:
                product_id = int(input("Ingrese el ID del producto a consultar: "))
                quantity = int(input("Ingrese la cantidad a verificar: "))
                
                result = self.check_inventory(product_id, quantity)
                
                if result == "NO_CONNECTION":
                    print("Error: No hay conexión con el servicio de inventario.")
                elif result == "INVALID_QUANTITY":
                    print("Error: La cantidad debe ser un número positivo mayor que 0.")
                elif result == "PRODUCT_NOT_FOUND":
                    print(f"Error: El producto con ID {product_id} no existe en el inventario.")
                elif result == "AVAILABLE":
                    print(f"Verificación de inventario exitosa: Producto {product_id} disponible en la cantidad solicitada ({quantity}).")
                elif result == "INSUFFICIENT_QUANTITY":
                    available = self.inventory[product_id]
                    print(f"Verificación de inventario: Producto {product_id} no disponible en la cantidad solicitada. Solicitado: {quantity}, Disponible: {available}")
            except ValueError:
                print("Error: Por favor, ingrese números válidos.")

def main():
    store_service = StoreService()
    store_service.run()

if __name__ == "__main__":
    main()