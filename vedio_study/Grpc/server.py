import time

import grpc
import demo_pb2_grpc, demo_pb2
from concurrent import futures
import threading


class DemoServer(demo_pb2_grpc.DemoServiceServicer):
    def SendMessage(self, request, context):
        print(f'{request.message}')
        return demo_pb2.DemoResponse(message='dfgsdfg')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    demo_pb2_grpc.add_DemoServiceServicer_to_server(DemoServer(), server)

    server.add_insecure_port('[::]:9920')
    server.start()
    print('Server 2 started to listen...')
    server.wait_for_termination()


def on_quote():
    time.sleep(10)
    print('send qoute')
    channel = grpc.insecure_channel('localhost:50052')
    stub = demo_pb2_grpc.DemoServiceStub(channel)
    for i in range(10):
        time.sleep(1)
        response = stub.SendMessage(demo_pb2.DemoRequest(message='quote'))


# python /byt_pub/a_songbo/Grpc/server.py
if __name__ == '__main__':
    serve()

    # a = threading.Thread(target=on_quote,)
    # b = threading.Thread(target=serve,)
    #
    # a.start()
    # b.start()
    # a.join()
    # b.join()



