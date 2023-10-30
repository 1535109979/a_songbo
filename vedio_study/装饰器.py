# 闭包
import time


def set_ab(a, b):
    def cal(x):
        return a * x + b

    return cal


cal1 = set_ab(1, 1)
cal2 = set_ab(2, 1)

# print(cal1(3))
# print(cal2(3))


# 带参数的装饰器

def timeit(iteration):
    def inner(f):
        def wrapper(*args, **kwargs):
            start = time.time()
            for _ in range(iteration):
                res = f(*args, **kwargs)
            print(time.time() - start)
            return res
        return wrapper

    return inner


@timeit(1000)
def double(x):
    return x * 2
# double(2)

# 装饰器的作用等价于
# def double(x):
#     return x * 2
# inner = timeit(1000)
# double = inner(double)
# double(2)


# 类的装饰器

def add_str(cls):
    def __str__(self):
        return str(self.__dict__)
    cls.__str__ = __str__
    return cls


@add_str
class MyObject:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# print(MyObject(1, 2))

# 装饰器的作用等价于
# MyObject = add_str(MyObject)
# m = MyObject(1, 2)
# print(m)


# 把装饰器封装到类里

class Decorators:
    # 写在这里可以通过  Decorators.log_function  无需实例化调用
    def log_function(func):
        def wrapper(*args, **kwargs):
            # print(f'func start:args={args}')
            ret = func(*args, **kwargs)
            # print(f'func end!')
            return ret
        return wrapper

    # 调用同一个类的方法作为装饰器，需要把方法写在上面，作为类的辅助函数
    @log_function
    def fib(self, n):
        if n <= 1:
            return 1
        return self.fib(n - 1) + self.fib(n - 2)

    log_function = staticmethod(log_function)   # 加上这个，可以通过类的对象来调用这个方法


d = Decorators()
print(d.fib(5))


@d.log_function
# @Decorators.log_function
def fib(n):
    if n <= 1:
        return 1
    return fib(n - 1) + fib(n - 2)


print(fib(5))

