from datetime import datetime

from celery_task import send_msg, send_email

v1 = datetime(2023, 10, 19, 17, 3, 00)
v2 = datetime.utcfromtimestamp(v1.timestamp())

result = send_msg.apply_async(args=['yan', ], eta=v2)
print(result.id)
