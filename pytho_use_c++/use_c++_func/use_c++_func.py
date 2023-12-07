import ctypes

ll = ctypes.cdll.LoadLibrary
lib = ll('./hello.so')
lib.main()


