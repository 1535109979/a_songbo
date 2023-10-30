import consul
import grpc
import calculator_pb2_grpc
import calculator_pb2
from calculator_pb2_grpc import CalculatorStub
from calculator_pb2 import *
from concurrent import futures

class Calculator(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        sum = request.num1 + request.num2
        return calculator_pb2.AddResponse(sum=sum)

c = consul.Consul()
service_id = "your_service_id"
service_name = "your_service_name"
service_address = "localhost"
service_port = 8500

# 将服务注册到Consul中
c.agent.service.register(
    name=service_name,
    service_id=service_id,
    address=service_address,
    port=service_port,
    check=consul.Check.tcp(service_address, service_port, interval="10s", timeout="5s")
)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
server.add_insecure_port("{}:{}".format(service_address, service_port))
server.start()
server.wait_for_termination()