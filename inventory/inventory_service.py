import pika
import json

class InventoryService:
    def __init__(self, host='localhost'):
        self.host = host
        self.queue_name = 'inventory_updates'

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

    def update_inventory(self, product_id, quantity):
        self.connect()
        message = json.dumps({'product_id': product_id, 'quantity': quantity})
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=message)
        print(f"Actualización de inventario enviada: Producto {product_id}, Cantidad {quantity}")
        self.close()

def main():
    inventory_service = InventoryService()
    inventory_service.update_inventory(123, 10)  # Product 123 has 10 units
    inventory_service.update_inventory(456, 5)   # Product 456 has 5 units

if __name__ == "__main__":
    main()