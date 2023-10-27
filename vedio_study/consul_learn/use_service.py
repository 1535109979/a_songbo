import grpc
from dns import resolver
from dns.exception import DNSException
# import test_pb2_grpc
# import test_pb2
import calculator_pb2
import calculator_pb2_grpc
# 连接consul服务，作为dns服务器


consul_resolver = resolver.Resolver()
consul_resolver.port = 8500
consul_resolver.nameservers = ["127.0.0.1"]


def get_ip_port(server_name):
    # try:
    answers = consul_resolver.resolve(f'{server_name}.service.consul', 'A')
    print(answers)
    # except DNSException:
    #     return None, None
    # return [rdata.address for rdata in answers]


ip, port = get_ip_port("my_service")
print(ip,port)
quit()
# channel = grpc.insecure_channel(f"{ip}:{port}")

channel = grpc.insecure_channel("localhost:12006")
stub = calculator_pb2_grpc.CalculatorStub(channel)
ret = stub.Add(calculator_pb2.AddRequest(num1=14,num2=12))
print(ret)


my_list = ['hello', 'world']
my_string = ''.join(my_list)  # 将列表连接为一个字符串

# 现在你可以将 my_string 传递给gRPC方法
response = stub.MyGRPCMethod(my_string.encode('utf-8'))



# 将目标字符串转换为字节流
target = 'localhost:50051'
target_bytes = target.encode('utf-8')

# 创建channel对象并使用它来调用gRPC方法
channel = grpc.insecure_channel(target_bytes)
stub = helloworld_pb2_grpc.GreeterStub(channel)
response = stub.SayHello(helloworld_pb2.HelloRequest(name='world'))
print(response.message)


services = ['192.168.1.100:50051', '192.168.1.101:50051']
target = ','.join(services)  # 将列表连接为一个字符串

# 现在你可以将 target 传递给 gRPC 的 Channel() 方法
channel = grpc.insecure_channel(target.encode('utf-8'), options=[
    ('grpc.lb_policy_name', 'round_robin'),
    ('grpc.enable_retries', True),
    ('grpc.keepalive_time_ms', 10000),
    ('grpc.keepalive_timeout_ms', 5000),
    ('grpc.keepalive_permit_without_calls', True),
])
