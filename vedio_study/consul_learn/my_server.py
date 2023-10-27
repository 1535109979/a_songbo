import grpc
import calculator_pb2
import calculator_pb2_grpc
from concurrent import futures
import consul


def register(server_name, ip, port):
    c = consul.Consul()
    print(f"开始注册服务{server_name}")
    c.agent.service.register(
            name=server_name,
            service_id=server_name,
            address=ip,
            port=int(port),
            check=consul.Check.tcp("localhost", port=int(port), interval='10s',timeout='20s',deregister='30s')
            # check=consul.Check.grpc(grpc="localhost:12003",interval='3s')
        )


class Calculator(calculator_pb2_grpc.CalculatorServicer):
    def Add(self, request, context):
        print('ip地址：',context.peer())
        sum = request.num1 + request.num2
        return calculator_pb2.AddResponse(sum=sum)
        # for i in range(sum):
        #     res = calculator_pb2.AddResponse(sum=i)
        #     context.write(res)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
calculator_pb2_grpc.add_CalculatorServicer_to_server(Calculator(), server)
server.add_insecure_port('[::]:8501')

server.start()
server.wait_for_termination()


