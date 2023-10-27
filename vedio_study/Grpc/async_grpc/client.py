import asyncio
import time

import grpc

import stream_data_pb2, stream_data_pb2_grpc


class ClientStream:

    def __init__(self):
        self.channel = grpc.aio.insecure_channel("127.0.0.1:8659")
        self.sub = stream_data_pb2_grpc.StreamRpcStub(channel=self.channel)

    async def GetServerResult(self):
        # 异步调用rpc
        result = await self.sub.GetServerResult(stream_data_pb2.Requests(data="aaa"))
        print("GetServerResult result: ", result)

    # 单向流
    async def GetServerStream(self):
        # 获取单向流对象
        stream_client = self.sub.GetServerStream(stream_data_pb2.Requests(data="aaa"))
        # 通过异步for 循环获取响应数据
        async for i in stream_client:
            print("GetServerStream result : ", i)

    # 单向流
    async def ClientSendStream(self):
        # 获取单向流对象
        stream_client = self.sub.ClientSendStream()
        for i in range(10):
            await stream_client.write(stream_data_pb2.Requests(data="{}".format(i)))
        # 客户端使用异步发送流数据需要手动关闭，客户端使用同步调用发送流数据的时候是不需要手动关闭的:
        # 同步调用代码如下：
        # def Client_send_stream(self):
        #     index = 0
        #     while 1:
        #         index += 1
        #         yield stream_data_pb2.Requests(data="{}".format(index))
        #         # time.sleep(1)
        #         if index == 10:
        #             break
        #     print("已结束")
        # result = self.stub.ClientSendStream(Client_send_stream())

        # 个人猜测是因为同步调用是通过另一个函数方法通过yield生成发送数据，当这个yield生成发送数据方法结束后在
        # ClientSendStream中封装了 自动关闭的功能， 因为同步调用执行完 result 这行代码就可以关闭这次调用了
        # 而异步调用是不会堵塞的， 就意味着，无法在 stream_client = self.sub.ClientSendStream() 期间进行封装
        # 关闭功能，如果在 stream_client 这个流对象生命期间封装 关闭功能的话， 这个ClientSendStream方法在发送完流数据后
        # 可能会做一下其他的事情， 如： 我在发送完流数据后做一些耗时的扫尾工作，导致这次的rpc调用迟迟无法结束，这会占用服务器
        # 的资源，所以，在 stream_client 生命周期做关闭功能封装也是不现实的，所以就需要我们手动关闭

        await stream_client.done_writing()
        data = await stream_client
        print("ClientSendStream result: ", data)

    # 双向流客户端往服务器发送流数据
    async def ClientSendStreamServer(self, stream_client):
        for i in range(6):
            print("正在往服务器发送流式数据： ", i, time.time())
            await stream_client.write(stream_data_pb2.Requests(data="send data {}".format(i)))
            await asyncio.sleep(2)
        await stream_client.done_writing()

    # 双向流 接收服务器发送的流数据
    async def RecvServerStream(self, stream_client):
        async for i in stream_client:
            print("接收到服务器流式数据： ", i)
        print("数据接收结束", time.time())

    # 双向流
    async def ServerClientStream(self):
        stream_client = self.sub.ServerClientStream()
        # 将 接收流、发送流 方法添加到事件循环中， 等待这两个方法结束
        await asyncio.gather(
            self.ClientSendStreamServer(stream_client),
            self.RecvServerStream(stream_client)
        )


async def main():
    client_stream = ClientStream()

    # await client_stream.GetServerResult()

    # await client_stream.ClientSendStream()

    await client_stream.GetServerStream()

    # await client_stream.ServerClientStream()


if __name__ == '__main__':
    client_stream = ClientStream()
    asyncio.run(main())

