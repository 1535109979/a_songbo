import asyncio
import time

import pika


credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# 声明一个队列
channel.queue_declare(queue='hello')

# 发布消息
message = 'Hello, RabbitMQ! 1'
channel.basic_publish(exchange='', routing_key='hello', body=message)

# 打印发布的消息
print(" [x] Sent:", message)

# 关闭连接
connection.close()
