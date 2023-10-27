import time
from multiprocessing import Process, Pipe
from multiprocessing.connection import wait


def child(conn):
    conn.send('Hello')
    conn.close()


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=child, args=(child_conn,))
    p.start()

    print(parent_conn.recv())

    # 等待两个连接上有消息到达
    # ready_conns = wait([parent_conn, child_conn])
    # for conn in ready_conns:
    #     if conn == parent_conn:
    #         print('Parent received:', parent_conn.recv())
    #     elif conn == child_conn:
    #         print('Child sent:', child_conn.recv())

    p.join()
