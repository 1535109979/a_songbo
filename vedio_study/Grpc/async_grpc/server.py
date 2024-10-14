import asyncio
import time

import grpc

from a_songbo.Grpc.async_grpc import stream_data_pb2, stream_data_pb2_grpc


class AsyncStreamServer(stream_data_pb2_grpc.StreamRpcServicer):
    # 一元调用
    async def GetServerResult(self, request, context):
        print("GetServerResult 服务器接收到的数据是： ", request.data)
        return stream_data_pb2.Reply(result="hell tnan")

    # 服务器发送流式数据给客户端
    async def GetServerStream(self, request, context):
        print("GetServerStream 服务器接收到的数据是： ", request.data)
        for i in range(10):
            # 通过context rpc上下文 来异步发送流数据
            await context.write(stream_data_pb2.Reply(result="{}".format(i)))
        # self.context_list.append(context)
        # print('get client')
        # while not context.done():
        #     pass

    async def on_quote(self, data):
        for context in self.context_list:
            await context.write(stream_data_pb2.Reply(result="{}".format('sdf')))

    # 服务器接收客户端流式数据
    async def ClientSendStream(self, request_iterator, context):
        async for i in request_iterator:
            print(i)
            await asyncio.sleep(1)
        print("结束： ", time.time())
        return stream_data_pb2.Reply(result="aabbbbbb")

    # 服务端发送stream数据协程
    async def ServerSendStreamClient(self, context):
        for i in range(5):
            print("服务器正在往客户端流式发送数据： ", i)
            await context.write(stream_data_pb2.Reply(result="{}".format(i)))
            await asyncio.sleep(1)

    # 服务器接收客户端stream 数据协程
    async def RecvClientStream(self, request_iterator):
        async for i in request_iterator:
            print("服务器接收到客户端流式数据： ", i)
        print("数据接收结束")

    # 双向流
    async def ServerClientStream(self, request_iterator, context):
        # 添加两个协程任务，等待协程任务执行完毕
        await asyncio.gather(
            self.ServerSendStreamClient(context),
            self.RecvClientStream(request_iterator)
        )


async def main():
    # 创建grpc 异步服务器
    g = grpc.aio.server()
    g.add_insecure_port("0.0.0.0:8659")
    stream_data_pb2_grpc.add_StreamRpcServicer_to_server(AsyncStreamServer(), g)
    await g.start()
    await g.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(main())

