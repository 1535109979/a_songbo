import grpc
import calculator_pb2
import calculator_pb2_grpc


options = (("grpc.lb_policy_name", "round_robin"),)

# channel = grpc.insecure_channel("ipv4:127.0.0.1:8501",options=options)
channel = grpc.insecure_channel("ipv4:127.0.0.1:8501")
stub = calculator_pb2_grpc.CalculatorStub(channel)
response = stub.Add(calculator_pb2.AddRequest(num1=10, num2=20))
print(response)
print(response.sum)




