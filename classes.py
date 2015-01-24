__author__ = 'Malgorzata Targan'
#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from math import pi, sin
from numpy import linspace, arange, log10 , sqrt , mean, blackman
from numpy.random.mtrand import normal
from numpy.fft import fft, fftshift
from scipy.signal import butter, lfilter, freqz
import matplotlib.pylab as m

# define max modulating frequency [Hz]
MAX_MOD_FREQ = 1000.0

# define coefficient that tells how many times carrier freq must be bigger than modulating
CARR_TO_MOD = 20.0

# define max carrier frequency [Hz]
MAX_CARR_FREQ = 1000000000

# define snr [dB]
SNR = 20.0

# define coefficient for setting sampling frequency
FS_TO_CARR = 4.0

# define min dB level on spectrum plot

MIN_DB = -40


class Dev: # base class for all modules
    def __init__(self, name):
        self._name = str(name)
        print("New dev, called", self._name)

        self._output = None
        self._input = None
        self._out_sig = []
        self._client = []

# connect other device to output
    def connect(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot connect...")
        else:
            self._output = dev
            dev._input = self
            print(self._name, "->", dev._name, "Connected...")

# notify device and give it access to data
    def notify(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot register...")
        else:
            dev._client.append(self)
            print(self._name, "->", dev._name, "Registered...")

    def run(self): pass


class Plotter(Dev):
    def run(self):
        for i in range(len(self._client)):
            m.figure(self._client[i]._name + "Output")
            m.plot(Generator._time , self._client._out_sig)

    def plot(x, y, title):
            m.figure(title)
            m.plot(y , x)


class Generator(Dev):
    def __init__(self, name):
        Dev.__init__(self,name)
        self._carr_sig = []
        self._time = None  # time vector
        self._fc = None  # carrier frequency
        self._fm = None  # modulating signal frequency
        self._am = None  # modulating signal amplitude
        self._ac = None  # carrier amplitude
        self._fs = None  # sampling frequency

# collect input data and set range
    def input_data(self):

        print("Input Modulation Frequency:")
        self._fm = self.verify_data(1, MAX_MOD_FREQ)
        while 0 >= self._fm:
            self._fm = self.verify_data(1, MAX_MOD_FREQ)
            pass

        print("Input Carrier Frequency (at least : " + str(CARR_TO_MOD) + " times as modulating frequency)")
        self._fc = self.verify_data(CARR_TO_MOD*self._fm)
        while 0 >= self._fc:
            self._fc = self.verify_data(CARR_TO_MOD*self._fm)
            pass

        print("Input Modulation Amplitude:")
        self._am = self.verify_data(1)
        while 0 >= self._am:
            self._am = self.verify_data(1)
            pass

        print("Input Modulation Index:")
        temp_im = self.verify_data(0, 1)
        while 0 >= temp_im:
            temp_im = self.verify_data(0, 1)
            pass

        self._ac = self._am/temp_im
        self._fs = FS_TO_CARR*self._fc

# verify if data is in allowed range
    @staticmethod
    def verify_data(data_min, data_max=sys.maxsize-1):
        try:
            buffer = float(input(" "))
        except ValueError:
            print("Not a number")
            return -1
        except NameError:
            print("Can't be empty")
            return -2
        if(buffer <= float(data_max)) and (buffer >= float(data_min)):
            return buffer
        else:
            print("Out of range")
            return -3

# generate signals - carrier and modulating
    def run(self):
        self._time = arange(0, FS_TO_CARR/self._fm, 1.0/(self._fs))
        for t in self._time: self._out_sig.append(self._am*sin(2*pi*self._fm*t))
        for t in self._time: self._carr_sig.append((self._ac*sin(2*pi*self._fc*t)))
        Plotter.plot(self._carr_sig, self._time, "Carrier Output")


gen = Generator("Generator")


class SpectrumAnalyzer(Dev):
    def __init__(self, name):
        Dev.__init__(self, name);
        self._spectrum = []
        self._freq = []


    def run(self):
        for i in range(len(self._client)):
            self._spectrum = fftshift(fft(self._client[i]._out_sig*blackman(len(self._client[i]._out_sig))))
            self._spectrum = self._spectrum/max(abs(self._spectrum)) # normalization
            self._freq = arange(0,(gen._fs)/2,(gen._fs)/len(self._spectrum))
            self._spectrum = 20*log10(abs(self._spectrum[len(self._spectrum)/2:len(self._spectrum)]))
            self.scale()
            m.figure("Magnitude " + self._client[i]._name)
            m.plot(self._freq , self._spectrum,".-")


    def scale(self):
        flag = 0;
        for n in range(len(self._spectrum)):
            if self._spectrum[n] > MIN_DB and 0 == flag:
                min_idx = n
                flag = 1;
            else:
                if self._spectrum[n] > MIN_DB:
                    max_idx = n

        if min_idx > 20:
            min_idx -= 20
        else:
            min_idx = 0

        if max_idx < len(self._spectrum) - 20:
            max_idx += 20
        else:
            max_idx = len(self._spectrum)

        self._spectrum = self._spectrum[min_idx:max_idx]
        self._freq = self._freq[min_idx:max_idx]



spec = SpectrumAnalyzer("SpectrumAnalyzer")


class Modulator(Dev):


    def run(self):
        #AM - suppressed carrier, modulate input signal
        for t, s in zip(self._input._carr_sig, self._input._out_sig): self._out_sig.append(t*s)
        m.figure("Modulated")
        m.plot(self._input._time, self._out_sig)






