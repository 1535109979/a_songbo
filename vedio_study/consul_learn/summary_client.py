import grpc
import calculator_pb2
import calculator_pb2_grpc
import consul
import sys


class MyClient():
    @classmethod
    def query_health_services(cls,ip='localhost',port='8500',service_name='order_server5'):
        c = consul.Consul(host=ip,port=port)
        nodes = c.health.service(service_name, passing=True)[1]
        services = [node['Service']['Address'] + ':' + str(node['Service']['Port']) for node in nodes]
        print('健康节点：',services)

        options = (("grpc.lb_policy_name", "round_robin"),)
        target = ','.join(services)
        channel = grpc.insecure_channel('ipv4:'+target, options=options)
        return channel

    @classmethod
    def run(cls,ip='localhost',port='8501',service_name='order_server5',x='10',y='20'):
        service_channel = cls.query_health_services(ip,int(port),service_name)
        # channel = grpc.insecure_channel(service)
        stub = calculator_pb2_grpc.CalculatorStub(service_channel)
        response = stub.Add(calculator_pb2.AddRequest(num1=int(x), num2=int(y)))
        print(response.sum)


if __name__ == '__main__':
    MyClient.run()

    # MyClient.run(ip=sys.argv[1], port=sys.argv[2], service_name=sys.argv[3],x=sys.argv[4],y=sys.argv[5])
