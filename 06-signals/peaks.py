#!/usr/bin/env python3
from sys import argv
import numpy
import struct
import wave

file = wave.open(argv[1], 'r')

channels = file.getnchannels()
frameRate = file.getframerate()
numberOfFrames = file.getnframes()

min = numpy.inf
max = -numpy.inf

for _ in range(numberOfFrames // frameRate):
    frame = file.readframes(frameRate)

    if channels == 1:
        window = struct.unpack(str(frameRate) + 'h', frame)
    else:
        window = struct.unpack(str(2 * frameRate) + 'h', frame)

    arrayWindow = numpy.array(window)
    if channels == 2:
        newWindow = []
        win = arrayWindow.reshape(-1,2)
        for array in win:
            newWindow.append( (array[0] + array[1] ) / 2 )
        arrayWindow = numpy.array(newWindow)

    amplitudes = numpy.abs( numpy.fft.rfft(arrayWindow) / frameRate )

    for frequency, amplitude in enumerate(amplitudes):
        if amplitude >= 20 * numpy.average(amplitudes):
            if frequency < min:
                min = frequency

            if frequency > max:
                max = frequency

if min == numpy.inf or max == -numpy.inf:
    print("no peaks")
else:
    print("low = " + str(min) + ", high = " + str(max))
