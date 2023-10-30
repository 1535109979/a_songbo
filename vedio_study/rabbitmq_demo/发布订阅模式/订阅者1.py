import pika

credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='m1', exchange_type='direct')

result = channel.queue_declare(exclusive=True, queue='')
queue_name = result.method.queue

channel.queue_bind(exchange='m1', queue=queue_name, routing_key='rk1')
channel.queue_bind(exchange='m1', queue=queue_name, routing_key='rk2')


def callback(ch, method, properties, body):
    print(" [x] Received:", body)


channel.basic_consume(queue=queue_name, on_message_callback=callback)
channel.start_consuming()

