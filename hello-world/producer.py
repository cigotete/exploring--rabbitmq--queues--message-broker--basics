import pika
import sys

# Establish RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declaration queue
channel.queue_declare(queue='hello')

# Obtaining message from command line or using default message
message = ' '.join(sys.argv[1:]) or "Hello World!"

# Publishing message
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)

print(f" [x] Sent '{message}'")

# Closing connection
connection.close()