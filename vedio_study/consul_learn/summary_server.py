import grpc
import calculator_pb2
import calculator_pb2_grpc
from concurrent import futures
import consul
import sys


class Calculator(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        sum = request.num1 + request.num2
        return calculator_pb2.AddResponse(sum=sum)


class MyServer():
    @classmethod
    def register(cls,server_name, ip, port):
        c = consul.Consul(host=ip,port=port)
        print(f"开始注册服务{server_name}")
        c.agent.service.register(
            name=server_name,
            service_id=server_name,
            address=ip,
            port=int(port),
            check=consul.Check.tcp("localhost", port=int(port), interval='10s')
        )

    @classmethod
    def run(cls,service_name="order_server5",ip="localhost",port='8501'):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
        server.add_insecure_port(f'[::]:{int(port)}')
        cls.register(service_name, ip, int(port))
        server.start()

        server.wait_for_termination()


if __name__ == '__main__':
    # MyServer.run(service_name=sys.argv[1], ip=sys.argv[2], port=sys.argv[3])
    MyServer.run()
