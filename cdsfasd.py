from datetime import datetime


def pro():
    t = 1.6988215675e+18 / 1e9

    print(t)
    print(type(t))

    dt = datetime.fromtimestamp(t)

    print(dt)


def prorce(func):
    print(func.__name__)


prorce(pro)
