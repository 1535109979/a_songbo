# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: demo.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndemo.proto\x12\tgrpc_demo\"\x1e\n\x0b\x44\x65moRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1f\n\x0c\x44\x65moResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2O\n\x0b\x44\x65moService\x12@\n\x0bSendMessage\x12\x16.grpc_demo.DemoRequest\x1a\x17.grpc_demo.DemoResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'demo_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _DEMOREQUEST._serialized_start=25
  _DEMOREQUEST._serialized_end=55
  _DEMORESPONSE._serialized_start=57
  _DEMORESPONSE._serialized_end=88
  _DEMOSERVICE._serialized_start=90
  _DEMOSERVICE._serialized_end=169
# @@protoc_insertion_point(module_scope)