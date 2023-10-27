from concurrent import futures

import grpc

from a_songbo.Grpc.server import DemoServer
import demo_pb2_grpc,demo_pb2


class DemoClient:

    def send_message(self, message):
        channel = grpc.insecure_channel('localhost:9920')
        stub = demo_pb2_grpc.DemoServiceStub(channel)
        response = stub.SendMessage(demo_pb2.DemoRequest(message=message))
        print(f'server response: {response.message}')

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        demo_pb2_grpc.add_DemoServiceServicer_to_server(DemoServer(), server)

        server.add_insecure_port('[::]:50052')
        server.start()
        print('Client started to listen...')
        server.wait_for_termination()


if __name__ == '__main__':
    client = DemoClient()
    client.send_message('account_id')
    # client.serve()

