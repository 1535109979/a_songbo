import time


# 使用装饰器计算程序运行时间
def time_consume(func):
    def cal_consume():
        print('开始计算时间')
        start_time = time.time()
        func()
        end_time = time.time()
        print('计时结束')
        return print(f'耗时：{end_time - start_time :.2f}')
    return cal_consume


@time_consume
def my_func():
    time.sleep(2)


if __name__ == '__main__':
    my_func()




