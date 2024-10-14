import random
import time

import grpc
import market_demo_pb2,market_demo_pb2_grpc


def subscribe_data():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = market_demo_pb2_grpc.DataServiceStub(channel)
        request = market_demo_pb2.DataRequest(request_id="test_request 2222")
        responses = stub.SubscribeData(request)
        for response in responses:
            print("Received response: {}".format(response.data))


def send_stream_demo():
    while 1:
        time.sleep(1)
        data = str(random.random())
        yield market_demo_pb2.StreamRequest(data=data)


def send_stream_client():
    channel = grpc.insecure_channel('localhost:50051')
    stub = market_demo_pb2_grpc.DataServiceStub(channel)

    # responses = stub.TestClietSendStream(send_stream_demo())   # 客户端流式发送数据
    # print(responses.result)

    responses = stub.TwoWayStream(send_stream_demo())     # 客户端流式发送数据
    for res in responses:                                        # 流式接受数据
        print(res.result)


if __name__ == '__main__':
    subscribe_data()

    # send_stream_client()