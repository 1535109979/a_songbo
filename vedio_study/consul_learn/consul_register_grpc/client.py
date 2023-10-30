import consul
import grpc

import calculator_pb2
from calculator_pb2_grpc import CalculatorStub
from calculator_pb2 import *


class ConsulGrpcBalancer:
    def __init__(self, service_name):
        self.service_name = service_name
        self.consul = consul.Consul()
        self.last_index = None

    def get_channel(self):
        services, self.last_index = self.consul.health.service(
            self.service_name, index=self.last_index, passing=True
        )
        instances = []
        for service in services:
            instances.append("{}:{}".format(service["Service"]["Address"], service["Service"]["Port"]))
        channel = grpc.experimental.insecure_channel(instances, options=[
            ('grpc.lb_policy_name', 'round_robin'),
            ('grpc.enable_retries', True),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
        ])
        return channel


def main():
    balancer = ConsulGrpcBalancer("your_service_name")
    channel = balancer.get_channel()
    stub = CalculatorStub(channel)
    response = stub.Add(calculator_pb2.AddRequest(num1=14,num2=12))
    print(response.message)


if __name__ == "__main__":
    main()