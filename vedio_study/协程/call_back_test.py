from concurrent.futures import Future, ThreadPoolExecutor
import time


count = 1

def func(arg1,a):
    # 执行耗时操作的函数
    print(arg1)
    global count
    count += 1
    print('cout:', count)
    return arg1

# 创建Future对象
future = Future()

# 注册回调函数
def callback(future_obj):
    result = future_obj.result()
    print(result)

future.add_done_callback(callback)

# 创建线程池
pool = ThreadPoolExecutor(max_workers=5)
# 提交任务到线程池
li = [1, 2, 3, 4]

for l in li:
    pool.submit(func, l, 22)

# 设置Future对象的结果
# future.set_result(333)
# 关闭线程池
pool.shutdown(wait=True)



