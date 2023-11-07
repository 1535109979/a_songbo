import functools
import threading
import time


def class_synchronized(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_lock'):
            # 每个实例有自己的锁
            self._lock = threading.RLock()
        with self._lock:
            return func(self,*args, **kwargs)

    return wrapper


def func_synchronized(func):
    func.__lock__ = threading.RLock()

    @functools.wraps(func)
    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return lock_func


def instance_synchronized(func):

    @functools.wraps(func)
    def lock_func(*args, **kwargs):
        if args:
            _self = args[0]
            if isinstance(_self, object):
                if hasattr(_self, "__instance_lock__"):
                    lock = _self.__instance_lock__
                else:
                    lock = threading.RLock()
                with lock:
                    return func(*args, **kwargs)

    return lock_func


class Account:
    def __init__(self, balance, account_name):
        self.account_name = account_name
        self.balance = balance

    @class_synchronized
    def draw(self, amount):
        name = threading.current_thread().name
        if self.balance >= amount:
            time.sleep(0.2)
            print(f'{name}取{self.account_name}钱成功')
            self.balance -= amount
            print(f'{name}余{self.account_name}额{self.balance}')
        else:
            print(f'{name}余{self.account_name}额不足')


if __name__ == '__main__':
    account1 = Account(1000, '1')
    account2 = Account(1000, '2')

    for account in [account1, account2]:

        ta = threading.Thread(name='a', target=account.draw, args=(800,))
        tb = threading.Thread(name='b', target=account.draw, args=(800,))

        ta.start()
        tb.start()


