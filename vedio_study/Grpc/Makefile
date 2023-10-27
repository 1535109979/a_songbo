generate:
    python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ ./market_demo.proto


# python -m grpc_tools.protoc: 这是运行protobuf编译器的命令，使用Python模块grpc_tools.protoc来执行编译操作。
# -I./: 这是指定导入proto文件的搜索路径。.表示当前目录，即在当前目录中查找proto文件。
# --python_out=./: 这是指定生成的Python代码的输出路径。--python_out选项后面的./表示将生成的代码放在当前目录中。
# --grpc_python_out=./: 这是指定生成的gRPC Python代码的输出路径。--grpc_python_out选项后面的./表示将生成的代码放在当前目录中。
# ./trade_server.proto: 这是要编译的proto文件路径。./trade_server.proto表示在当前目录中查找名为trade_server.proto的proto文件进行编译。