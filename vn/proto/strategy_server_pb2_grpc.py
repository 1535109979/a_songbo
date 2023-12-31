# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from a_songbo.vn.proto import account_position_pb2 as account__position__pb2
from a_songbo.vn.proto import strategy_server_pb2 as strategy__server__pb2


class StrategyStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.on_account_update = channel.unary_unary(
                '/strategy_server.Strategy/on_account_update',
                request_serializer=account__position__pb2.AccountBook.SerializeToString,
                response_deserializer=strategy__server__pb2.FlagReply.FromString,
                )
        self.on_order_rtn = channel.unary_unary(
                '/strategy_server.Strategy/on_order_rtn',
                request_serializer=strategy__server__pb2.RtnRecord.SerializeToString,
                response_deserializer=strategy__server__pb2.FlagReply.FromString,
                )
        self.on_trade_rtn = channel.unary_unary(
                '/strategy_server.Strategy/on_trade_rtn',
                request_serializer=strategy__server__pb2.RtnRecord.SerializeToString,
                response_deserializer=strategy__server__pb2.FlagReply.FromString,
                )


class StrategyServicer(object):
    """Missing associated documentation comment in .proto file."""

    def on_account_update(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def on_order_rtn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def on_trade_rtn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_StrategyServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'on_account_update': grpc.unary_unary_rpc_method_handler(
                    servicer.on_account_update,
                    request_deserializer=account__position__pb2.AccountBook.FromString,
                    response_serializer=strategy__server__pb2.FlagReply.SerializeToString,
            ),
            'on_order_rtn': grpc.unary_unary_rpc_method_handler(
                    servicer.on_order_rtn,
                    request_deserializer=strategy__server__pb2.RtnRecord.FromString,
                    response_serializer=strategy__server__pb2.FlagReply.SerializeToString,
            ),
            'on_trade_rtn': grpc.unary_unary_rpc_method_handler(
                    servicer.on_trade_rtn,
                    request_deserializer=strategy__server__pb2.RtnRecord.FromString,
                    response_serializer=strategy__server__pb2.FlagReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'strategy_server.Strategy', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Strategy(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def on_account_update(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/strategy_server.Strategy/on_account_update',
            account__position__pb2.AccountBook.SerializeToString,
            strategy__server__pb2.FlagReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def on_order_rtn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/strategy_server.Strategy/on_order_rtn',
            strategy__server__pb2.RtnRecord.SerializeToString,
            strategy__server__pb2.FlagReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def on_trade_rtn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/strategy_server.Strategy/on_trade_rtn',
            strategy__server__pb2.RtnRecord.SerializeToString,
            strategy__server__pb2.FlagReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
