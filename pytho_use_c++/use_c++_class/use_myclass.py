import ctypes

ll = ctypes.cdll.LoadLibrary
lib = ll('./myclass.so')


lib.add()
quit()




