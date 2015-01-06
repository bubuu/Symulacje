__author__ = 'Gosia'
#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from math import pi, sin
from numpy import linspace, arange, log10 , sqrt , mean, blackman
from numpy.random.mtrand import normal
from numpy.fft import fft, fftshift
from scipy.signal import butter, lfilter, freqz
import matplotlib.pylab as m

class Dev: # klasa bazowa wszystkich modułów
    def __init__(self, name):
        self._name = str(name)
        print("New dev, called", self._name)

        self._output = None
        self._input = None
        self._client = []

    def __len__(self):
        return len(self._buffer)

    def connect(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot connect...")
        else:
            self._output = dev
            dev._input = self
            print(self._name, "->", dev._name, "Connected...")

    def notify(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot register...")
        else:
            dev._client.append(self)
            print(self._name, "->", dev._name, "Registered...")

    def run(self): pass


class InputData: # klasa bazowa
    def __init__(self, name):
        self._name = str(name)
        self._value = None



from random import random
# class Generator(Dev): # przykład klasy generatora
#     def run(self): self._buffer.append(random()-0.5)


# class Converter(Dev):  # przykład klasy konwertera
#     def run(self):
#         while len(self._input)>1:
#             x = self._input._buffer.pop()
#             y = self._input._buffer.pop()
#             self._buffer.append(complex(x ,y))

snr = 50
coeff = 10.0

fc = None
class Generator(Dev):
    def __init__(self, name):
        Dev.__init__(self,name)
        self._time = None
        self._carr_sig = []
        self._out_sig = []
        self._fc = None
        self._fm = None
        self._am = None
        self._im = None
        self._ac = None

    def input_data(self):
        print("Input Carrier Frequency:")
        self._fc = self.verify_data(1)
        while 0 >= self._fc:
            self._fc = self.verify_data(1)
            pass
        global fc
        fc = self._fc

        print("Input Modulation Frequency:")
        self._fm = self.verify_data(1)
        while 0 >= self._fm:
            self._fm = self.verify_data(1)
            pass

        print("Input Modulation Amplitude:")
        self._am = self.verify_data(1)
        while 0 >= self._am:
            self._am = self.verify_data(1)
            pass

        #todo: overthink 0 as min value
        print("Input Modulation Index:")
        self._im = self.verify_data(0, 1)
        while 0 >= self._im:
            self._im = self.verify_data(0, 1)
            pass

        self._ac = self._am/self._im

    def verify_data(self, data_min, data_max=sys.maxsize-1):
        try:
            buffer = float(input(" "))
        except ValueError:
            print("Not a number")
            return -1
        except NameError:
            print("Cant be empty")
            return -2
        if(buffer < float(data_max)) and (buffer > float(data_min)):
            return buffer
        else:
            print("Out of range")
            return -3

    def run(self):
        self._time = arange(0, coeff/self._fm, 1.0/(coeff*self._fc))
        for t in self._time: self._carr_sig.append((self._ac*sin(2*pi*self._fc*t)))
        for t in self._time: self._out_sig.append(self._am*sin(2*pi*self._fm*t))
        #for t in self._time: self._out_sig.append(self._am*sin(2*pi*self._fm*t)+self._am)

        m.figure("Carrier")
        m.plot(self._time, self._carr_sig)
        m.figure("Modulating")
        m.plot(self._time, self._out_sig)


class Modulator(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._out_sig = []

    def run(self):
        #AM - suppressed carrier
        for t, s in zip(self._input._carr_sig, self._input._out_sig): self._out_sig.append(t*s)
        #AM
        im = self._input._im
        am = self._input._am
        #for t, s in zip(self._input._carr_sig, self._input._out_sig): self._out_sig.append(t+t*s*im/am)
        print(self._out_sig)
        m.figure("Modulated")
        print(self._out_sig)
        m.plot(self._input._time, self._out_sig)


class Demodulator(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._out_sig = []

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def run(self):
        for s, t in zip(self._input._out_sig, self._client[0]._out_sig): self._out_sig.append(s*t)
        m.figure("Bez filtracji")
        m.plot(self._client[0]._time, self._out_sig)
        self._out_sig = self.butter_lowpass_filter(self._out_sig, 4*pi*self._client[0]._fm, 2*pi*coeff*fc)
        m.figure("Z filtracja")
        m.plot(self._client[0]._time, self._out_sig)


class Channel(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._out_sig = []
        self._sigma = None
        self._noise = []

    def run(self):
        length = len(self._input._out_sig)
        average = mean(self._input._out_sig)
        var = sum(abs(self._input._out_sig - average)**2)/length
        self._sigma = sqrt(var/2)*10**(-snr/20)
        self._noise = normal(0.0, self._sigma, length)
        print(self._noise)
        #for t, s in zip(self._noise, self._input._out_sig): self._out_sig.append(t+s)
        for t, s in zip(self._noise, self._input._out_sig): self._out_sig.append(s)
        print(self._out_sig)
        m.figure("Received")
        m.plot(self._client[0]._time, self._out_sig)


class Filter(Dev):
    def run(self):
        pass


class SpectrumAnalyzer(Dev):
    def run(self):
        for i in range(len(self._client)):
            spectrum = None
            spectrum = fftshift(fft(self._client[i]._out_sig*blackman(len(self._client[i]._out_sig))))
            spectrum = spectrum/max(abs(spectrum)) # normalizacja
            freq_line = arange(-(4*fc)/2,(4*fc)/2,(4*fc)/len(spectrum))
            m.figure("Magnitude " + self._client[i]._name)
            m.plot(freq_line , 20*log10(abs(spectrum )),".-")

# carr_freq = 0

#

gen = Generator("Generator")
mod = Modulator("Modulator")
chan = Channel("Channel")
spec = SpectrumAnalyzer("SpectrumAnalyzer")
demod = Demodulator("Demodulator")

gen.connect(mod)
gen.notify(chan)
mod.connect(chan)
gen.notify(spec)
mod.notify(spec)
chan.notify(spec)
demod.notify(spec)
chan.connect(demod)
gen.notify(demod)
gen.input_data()


gen.run()
mod.run()
chan.run()
demod.run()
spec.run()


m.show()


# gen = Generator("gen")
# conv = Converter("conv")
# gen.connect(conv)
#
# # symulacja pracy modułów
# for n in range(5): gen.run()
# conv.run()
#
# print(gen._buffer)
# print(conv._buffer)