import ctypes

ll = ctypes.cdll.LoadLibrary
lib = ll('./myclass.so')


lib.add()
quit()


# class myclass(lib):
#
#     def __init__(self):
#
#         self.add()
#
#
# if __name__ == '__main__':
#     myclass()

