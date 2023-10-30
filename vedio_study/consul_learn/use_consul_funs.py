import consul
import time
import requests
import sys


class UseConsul():
    c = consul.Consul(host='localhost',port=8500)

    @classmethod
    def register_one_service(cls,service_name="my_service",address='localhost',service_port='8500',check_interval="10s"):
        cls.c.agent.service.register(
            name=service_name,
            service_id=service_name,
            address=address,
            port=int(service_port),
            check=consul.Check.tcp("localhost", port=int(service_port), interval=check_interval)
        )

    @classmethod
    def unregister_one_service(cls,service_name="order_server5"):
        cls.c.agent.service.deregister(service_name)
        print(f"退出服务{service_name}")

    @classmethod
    def get_services_list(cls):
        # services = cls.c.catalog.service('order_server10')
        # print(services)
        services = cls.c.agent.services()
        for service in services:
            print(service)

    @classmethod
    def query_nodes(cls):
        nodes = cls.c.catalog.nodes()
        print(nodes)

    @classmethod
    def query_health_services(cls,service_name='order_server3'):
        nodes = cls.c.health.service(service_name, passing=True)[1]
        services = [node.get('Service').get('Address') + ':' + str(node.get('Service').get('Port')) for node in nodes]
        print(services)

    @classmethod
    def get_se(cls,service_instances):
        url = f'http://{service_instances[0]["ServiceAddress"]}:{service_instances[0]["ServicePort"]}/api/v1/endpoint'
        response = requests.get(url)
        print(response)

    @classmethod
    def query_members(cls):
        members = cls.c.agent.members()
        for member in members:
            print(member)

if __name__ == '__main__':
    if sys.argv[1] == 'rg':
        UseConsul.register_one_service(service_name=sys.argv[2], address=sys.argv[3], service_port=sys.argv[4],check_interval=sys.argv[5])
    elif sys.argv[1] == 'qa':
        UseConsul.get_services_list()
    elif sys.argv[1] == 'qh':
        UseConsul.query_health_services(service_name=sys.argv[2])
    elif sys.argv[1] == 'qm':
        UseConsul.query_members()
    elif sys.argv[1] == 'de':
        UseConsul.unregister_one_service(service_name=sys.argv[2])

    # UseConsul.register_one_service(service_name='order_server5')
    # UseConsul.unregister_one_service(service_name='order_server3')

    # service_instances = UseConsul.get_services_list()
    # service_instances = UseConsul.unregister_one_service()


    # service_instances = UseConsul.query_health_services('order_server5')
