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



def fifth(frequency_queue):
    '''
    processes the frequency queue as it comes in (a fifth of the input frequency)
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
        i = 0
        while(1):
            fifth = freq * pow(1.05945454545454545455, 7) * pow(2, 0)
            third = freq * pow(1.05945454545454545455, 4) * pow(2, 0)
            WAVEDATA = chr(int(math.sin(i / ((44100 / fifth) / math.pi)) * 127 + 128))
            outputstream.write(WAVEDATA)
            if(frequency_queue.empty() == False and int(math.sin(i / ((44100 / fifth) / math.pi)) * 127) == 0):
                while(frequency_queue.empty() == False):
                    freq = frequency_queue.get()
                i = 0
            WAVEDATA = chr(int(math.sin(i / ((44100 / third) / math.pi)) * 127 + 128))
            outputstream.write(WAVEDATA)
            
            i += 1


def input_thread(output_queue):
    how_fast = 5
    paudio = pyaudio.PyAudio()
    stream = paudio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    old_freq = 0
    while(1):
        time.sleep(1 / how_fast)
        data = stream.read(RATE / how_fast)
        indata = np.fromstring(data, dtype=np.int32)
        # Take the fft and square each value
        fft_data=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fft_data[1:].argmax() + 1
        thefreq = 0
        # use quadratic interpolation around the max
        if which != len(fft_data)-1:
            y_0,y_1,y_2 = np.log(fft_data[which-1:which+2:])
            x_1 = (y_2 - y_0) * .5 / (2 * y_1 - y_2 - y_0)
            # find the frequency and output it
            thefreq = (which+x_1)*RATE/(RATE / how_fast)
            
        else:
            thefreq = which*RATE/(RATE / how_fast)

        thefreq *= pow(2, 2)
        if(thefreq > 500):
            #while(thefreq < 700):
            #    thefreq *= 2
            
            
            if(abs(thefreq - old_freq) > 50):
                print(thefreq)
                print("difference was " + str(abs(thefreq - old_freq)))
                old_freq = thefreq
                print("Sent")
                output_queue.put(thefreq)

    

queue = Queue()
queue.put(600) # 600 is the frequency that we get to open with

output = Thread(target=fifth, args=(queue,))
output.start()

t_1 = Thread(target=input_thread, args=(queue,))
time.sleep(1)
t_1.start()

