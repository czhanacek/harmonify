import pyaudio
import wave
import numpy as np
import math
from multiprocessing import Queue
from threading import Thread
import time

CHUNK = 22050
FORMAT = pyaudio.paInt16
swidth = 4
CHANNELS = 2
RATE = 44100



def outputThread(frequencyQueue):
    while((frequencyQueue.empty()) == 0):
        p = pyaudio.PyAudio()
        outputstream = p.open(
            format=p.get_format_from_width(1),
            channels=1,
            rate=RATE,
            output=True)

        freq = frequencyQueue.get()
        print("Ran!")
        while(frequencyQueue.empty()):
            WAVEDATA = ''
            for i in range(44100):
                WAVEDATA += chr(int(math.sin(i / ((44100 / freq) / math.pi)) * 127 + 128))
            outputstream.write(WAVEDATA)


def inputThread(frequencyQueue):
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    oldFreq = 0
    while(1):
        time.sleep(0.1)
        data = stream.read(RATE/10)
        indata = np.fromstring(data, dtype=np.int16)
        # Take the fft and square each value
        fftData=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fftData[1:].argmax() + 1
        freqstring = "The freq is "
        thefreq = 0
        # use quadratic interpolation around the max
        if which != len(fftData)-1:
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            thefreq = (which+x1)*RATE/(RATE / 10)
            freqstring += str(thefreq) + " Hz"
        else:
            thefreq = which*RATE/(RATE/10)
            freqstring += str(thefreq) + " Hz"

        print(freqstring)
        if(thefreq > 100):
            if(abs(thefreq - oldFreq) > 50):
                thefreq *= 4
                oldFreq = thefreq
                print("Sent")
                q.put(thefreq * pow(1.05945454545454545455, 7))

    
q = Queue()
q.put(600)
time.sleep(0.1)
print("Hello")
t1 = Thread(target=inputThread, args=(q,))
t2 = Thread(target=outputThread, args=(q,))
t1.start()
time.sleep(1)
t2.start()

