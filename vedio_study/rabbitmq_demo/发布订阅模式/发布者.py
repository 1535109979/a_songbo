import pika

credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='m1', exchange_type='direct')

message = 'sdfasdfsdgsg'

channel.basic_publish(
    exchange='m1',
    routing_key='rk1',
    body=message,
)

connection.close()
