import pika

# Establish RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declaration queue
channel.queue_declare(queue='hello')

# Callback message process
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

# Config message consumption
channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Start consuming
channel.start_consuming()