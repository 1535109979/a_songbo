import pika

credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# 声明一个队列
channel.queue_declare(queue='hello')


# 回调函数，用于处理接收到的消息
def callback(ch, method, properties, body):
    print(" [x] Received:", body)


channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

# 开始接收消息
print(' [*] Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()
