from celery_task import send_msg, send_email
from celery.result import AsyncResult
from celery_task import cel


res = send_msg.delay('sdfas')
print(res.id)

res = send_email.delay('sdfas')
print(res.id)


# 查询结果

# async_result = AsyncResult(id='74066fd3-310e-48ce-bb17-35401037fe9c', app=cel)
#
# if async_result.successful():
#     result = async_result.get()
#     print(result)
# elif async_result.failed():
#     print('failed')
# else:
#     print(async_result.status)


