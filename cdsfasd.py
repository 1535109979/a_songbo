import numpy

a = range(1, 400)

rolling_window = 200


ma = numpy.convolve(a, numpy.ones(rolling_window) / rolling_window, mode="valid")

print(len(ma))

