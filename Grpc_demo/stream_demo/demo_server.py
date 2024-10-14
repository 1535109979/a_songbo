import time
from concurrent import futures
import grpc

import market_demo_pb2,market_demo_pb2_grpc


class DataService(market_demo_pb2_grpc.DataServiceServicer):

    def SubscribeData(self, request, context):
        index = 0
        while context.is_active():
            time.sleep(1)
            index += 1
            data = request.request_id
            # print(index,data)
            yield market_demo_pb2.DataResponse(data=f'dmeo {index} {data}')
            # context.write(market_demo_pb2.DataResponse(message=f"Sent  to client."))

    def TestClietSendStream(self,request_iterator,context):
        index = 0

        for request in request_iterator:
            print(request.data)

            if index == 10:
                break
            index += 1

        return market_demo_pb2.StreamResponse(result='ok')

    def TwoWayStream(self, request_iterator, context):
        for request in request_iterator:
            data = request.data
            print('get data %s'%data)
            yield market_demo_pb2.TwoWayStreamResponse(result='service send client %s' % data)


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_demo_pb2_grpc.add_DataServiceServicer_to_server(DataService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at port 50051...")
    server.wait_for_termination()