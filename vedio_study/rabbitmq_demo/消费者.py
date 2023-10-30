import pika

credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# 声明一个队列
channel.queue_declare(queue='hello')


# 回调函数，用于处理接收到的消息
def callback(ch, method, properties, body):
    print(" [x] Received:", body)

    # 有异常，放回队列
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='hello', on_message_callback=callback)

# 开始接收消息
print(' [*] Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()
