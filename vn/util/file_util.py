import os


def mk_if_not_exists(path: str):
    """创建文件夹，如果不存在"""
    if path:
        if not os.path.exists(path):
            os.makedirs(path)
    return path
