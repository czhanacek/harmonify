import pyaudio
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



def output_thread(frequency_queue):
    '''
    processes the frequency queue as it comes in
    '''

    # basically while the frequency queue isn't empty, which it should never be....
    # create a pyaudio instance. I'm pretty sure that we need one of these per function,
    # but we could also probably have a single, global instance of the pyaudio object.
    # Might be worth trying.
    p = pyaudio.PyAudio()
    
    outputstream = p.open( # this struct makes the place where we send audio.
        format=p.get_format_from_width(1),
        channels=1,
        rate=RATE,
        output=True)
    
    print("Ran!") # this is just a XC plug
    while(1):
        
        freq = frequency_queue.get() # get the most recent function in the queue. Should only run 
                                # the first time the function is run.
        WAVEDATA = ''
        i = 0
        while(frequency_queue.empty()):
            time.sleep(1/44100)
            WAVEDATA = chr(int(math.sin(i / ((44100 / freq) / math.pi)) * 127 + 128))
            outputstream.write(WAVEDATA)
            i += 1


def input_thread(frequency_queue):
    
    paudio = pyaudio.PyAudio()
    stream = paudio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    old_freq = 0
    while(1):
        time.sleep(0.1)
        data = stream.read(RATE/10)
        indata = np.fromstring(data, dtype=np.int16)
        # Take the fft and square each value
        fft_data=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fft_data[1:].argmax() + 1
        freqstring = "The freq is "
        thefreq = 0
        # use quadratic interpolation around the max
        if which != len(fft_data)-1:
            y_0,y_1,y_2 = np.log(fft_data[which-1:which+2:])
            x_1 = (y_2 - y_0) * .5 / (2 * y_1 - y_2 - y_0)
            # find the frequency and output it
            thefreq = (which+x_1)*RATE/(RATE / 10)
            freqstring += str(thefreq) + " Hz"
        else:
            thefreq = which*RATE/(RATE/10)
            freqstring += str(thefreq) + " Hz"
        print(freqstring)
        if(thefreq > 100):
            if(abs(thefreq - old_freq) > 50):
                old_freq = thefreq
                
                print("Sent")
                frequency_queue.put(thefreq * pow(1.05945454545454545455, 7))

    

que = Queue()
que.put(600) # 600 is the frequency that we get to open with
t_2 = Thread(target=output_thread, args=(que,))
t_2.start()

t_1 = Thread(target=input_thread, args=(que,))
time.sleep(1)
t_1.start()

