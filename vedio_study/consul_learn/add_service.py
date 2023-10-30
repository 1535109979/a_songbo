import time
import grpc
import consul
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc


class Calculator(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        sum = request.num1 + request.num2
        return calculator_pb2.AddResponse(sum=sum)


class MyServer():
    @classmethod
    def register_service(cls,service_name="myservice",address='localhost',service_port='8500',check_interval="10s"):
        c = consul.Consul()
        c.agent.service.register(
            name=service_name,
            service_id=service_name,
            address=address,
            port=int(service_port),
            check=consul.Check.tcp("localhost", port=int(service_port), interval=check_interval)
        )

    @classmethod
    def run_server(cls):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
        server.add_insecure_port('[::]:{}'.format(8500))
        cls.register_service("order_server1", "localhost", '8500')
        server.start()





def register(server_name, ip, port):
    c = consul.Consul()  # 连接consul 服务器，默认是127.0.0.1，可用host参数指定host
    print(f"开始注册服务{server_name}")
    check = consul.Check.tcp(ip, port, "10s")  # 健康检查的ip，端口，检查时间
    c.agent.service.register(server_name, f"{server_name}-{ip}-{port}",
                             address=ip, port=port, check=check)  # 注册服务部分
    print(f"注册服务{server_name}成功")


def unregister(server_name, ip, port):
    c = consul.Consul()
    print(f"开始退出服务{server_name}")
    c.agent.service.deregister(f'{server_name}-{ip}-{port}')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
    server.add_insecure_port('[::]:{}'.format(8501))
    register("order_server1", "localhost", 8500)
    server.start()
    try:
        while True:
            time.sleep(186400)
    except KeyboardInterrupt:
        unregister("order_server", "0.0.0.0", 8500)
        server.stop(0)


if __name__ == '__main__':
    MyServer.run_server()
    # serve()