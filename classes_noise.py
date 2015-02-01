__author__ = 'Malgorzata Targan'
#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
from math import pi, sin
from numpy import linspace, arange, log10 , sqrt , mean, blackman, var
from numpy.random.mtrand import normal
from numpy.fft import fft, fftshift
from scipy.signal import butter, lfilter, freqz, filtfilt
import matplotlib.pylab as m


# ------------------------------------------------------------------------
# ----------------------------- CONSTANTS --------------------------------
# ------------------------------------------------------------------------

# define max modulating frequency [Hz]
MAX_MOD_FREQ = 1000.0

# define coefficient that tells how many times carrier freq must be bigger than modulating
CARR_TO_MOD = 20.0

# define max carrier frequency [Hz]
MAX_CARR_FREQ = 1000000000

# define snr [dB]
SNR = 10.0

# define coefficient for setting sampling frequency
FS_TO_CARR = 35.5

# define coefficient for cut frequency
COEF_CUT_FREQ = 10.0

# define number of periods to be visible on plots
PER_NUM = 10.0

# define min dB level on spectrum plot
MIN_DB = -20

# ------------------------------------------------------------------------
# ------------------------------ CLASSES ---------------------------------
# ------------------------------------------------------------------------


# -------------------------------- DEV -----------------------------------

class Dev: # base class for all modules
    def __init__(self, name):
        self._name = str(name)
        print("New dev, called", self._name)

        self._output = None
        self._input = None
        self._generator = None
        self._out_sig = []


# connect other device to output
    def connect(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot connect...")
        else:
            self._output = dev
            dev._input = self
            print(self._name, "->", dev._name, "Connected...")

    def set_gen(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot connect generator...")
        else:
            self._generator = dev
            print(self._name, "->", dev._name, "Added...")

# add new device to plot signal list
    def notify(self, dev):
        if not isinstance(dev, Dev):
            print(self._name, "Wrong type, cannot register...")
        else:
            dev._client.append(self)
            print(self._name, "->", dev._name, "Registered...")

    def run(self): pass


# ------------------------------ PLOTTER -----------------------------------


class Plotter(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._client = []

    def run(self):

        m.figure("Carrier Signal Output")
        m.subplot(len(self._client), 1, 1)
        m.plot(self._generator._time[0:int(PER_NUM*FS_TO_CARR)], self._generator._carr_sig[0:int(PER_NUM*FS_TO_CARR)])
        m.ylim([min(self._generator._carr_sig) , max(self._generator._carr_sig)])
        m.xlim([0 , self._generator._time[int(PER_NUM*FS_TO_CARR)]])
        m.grid()
        m.figure("Modulating Signal Output")
        m.subplot(len(self._client), 1, 2)
        m.plot(self._generator._time, self._generator._out_sig)
        m.ylim([min(self._generator._out_sig) , max(self._generator._out_sig)])
        m.xlim([0 , max(self._generator._time)])
        m.grid()

        for i in range(len(self._client)):
            m.figure(self._client[i]._name + " Output")
            m.subplot(len(self._client), 1, i + 2)
            m.plot(self._generator._time , self._client[i]._out_sig)
            m.ylim([min(self._client[i]._out_sig) , max(self._client[i]._out_sig)])
            m.xlim([0 , max(self._generator._time)])
            m. xlabel("t[s]")
            m. ylabel("A[V]")
            m.grid()


# ------------------------ SPECTRUM ANALYZER -------------------------------


class SpectrumAnalyzer(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._spectrum = []
        self._freq = []
        self._client = []

    def run(self):
        for i in range(len(self._client)):
            # generate spectrum chart
            self._spectrum = fftshift(fft(self._client[i]._out_sig*blackman(len(self._client[i]._out_sig))))
            self._spectrum = self._spectrum/max(abs(self._spectrum)) # normalization
            self._freq = arange(0,(self._generator._fs)/2,(self._generator._fs)/len(self._spectrum))
            self._spectrum = 20*log10(abs(self._spectrum[len(self._spectrum)/2:len(self._spectrum)]))
            self.scale()
            m.figure("Magnitude " + self._client[i]._name)
            m.plot(self._freq , self._spectrum,".-")
            m.xlim([min(self._freq) , max(self._freq)])
            m. xlabel("f[Hz]")
            m. ylabel("E[dBc]")

            m.grid()

            # generate spectrogram
            m.figure ("Spectrogram " + self._client[i]._name)
            m.specgram (self._client[i]._out_sig , NFFT =128 , Fs=self._generator._fs , noverlap =127)
            m.ylim([0, self._generator._fs/2])
            m.xlim([0, PER_NUM/self._generator._fm])
            m.xlabel("t[s]")
            m.ylabel("f[Hz]")
            m.grid()


    def scale(self):
        min_idx = 0
        max_idx = len(self._spectrum)-1
        flag = 0
        for n in range(len(self._spectrum)):
            if self._spectrum[n] > MIN_DB and 0 == flag:
                min_idx = n
                flag = 1
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


# ---------------------------- GENERATOR -----------------------------------


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
        self._sigma = None

# collect input data and set range
    def input_data(self):

        print("Input Max Modulation Noise Frequency:")
        self._fm = self.verify_data(1, MAX_MOD_FREQ)
        while 0 >= self._fm:
            self._fm = self.verify_data(1, MAX_MOD_FREQ)
            pass

        print("Input Carrier Frequency (at least : " + str(CARR_TO_MOD) + " times as modulating frequency)")
        self._fc = self.verify_data(CARR_TO_MOD*self._fm)
        while 0 >= self._fc:
            self._fc = self.verify_data(CARR_TO_MOD*self._fm)
            pass

        print("Input Standard Deviation:")
        self._sigma = self.verify_data(1)
        while 0 >= self._sigma:
            self._sigma = self.verify_data(1)
            pass

        print("Input Modulation Index:")
        temp_im = self.verify_data(0, 1)
        while 0 >= temp_im:
            temp_im = self.verify_data(0, 1)
            pass

        self._fs = FS_TO_CARR*self._fc
        # save modulation index value
        self._ac = temp_im

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
        self._time = arange(0, PER_NUM/self._fm, 1.0/(self._fs))
        self._out_sig = normal(0.0, self._sigma, len(self._time))
        self._am = max(abs(self._out_sig))
        self._ac = self._am/self._ac
        for t in self._time: self._carr_sig.append((self._ac*sin(2*pi*self._fc*t)))


# ---------------------------- MODULATOR -----------------------------------


class Modulator(Dev):

    def run(self):
        #AM - suppressed carrier, modulate input signal
        for t, s in zip(self._generator._carr_sig, self._input._out_sig): self._out_sig.append(t*s)


# ------------------------------ CHANNEL -----------------------------------


class Channel(Dev):
    def __init__(self, name):
        Dev.__init__(self, name)
        self._sigma = None
        self._noise = []

    def run(self):
        length = len(self._input._out_sig)
        vars = var(self._input._out_sig)
        self._sigma = sqrt(vars)*10**(-SNR/20)
        self._noise = normal(0.0, self._sigma, length)
        for t, s in zip(self._noise, self._input._out_sig): self._out_sig.append(t+s)


# ------------------------------ FILTER ------------------------------------


# class for filtering objects, can be LPF, HPF and BPF
class Filter(Dev):
    def __init__(self, name, ftype):
        Dev.__init__(self, name)
        self._type = str(ftype)
    # implement butterworth filter
    def butter_filter(self, data, fs, lowcut, highcut=0, order=5):
        #btype = 'pass'
        b, a = self.butter_get_coeff(fs, lowcut, highcut, order=order)
        y = filtfilt(b, a, data)
        return y

    def butter_get_coeff(self, fs, cut1, cut2, order=5):

        nyq = 0.5 * fs
        cut1 /= nyq
        cut2 /= nyq
        if 'high' == str(self._type):
            b, a = butter(order, cut1, btype='high')
        elif 'band' == str(self._type):
            b, a = butter(order, [cut1, cut2], btype='band')
            m.figure()
            order = 5
            c, d = butter(order, [cut1, cut2], str(self._type))
            w, h = freqz(c, d, worN=2000)
            m.plot((fs * 0.5 / pi) * w, abs(h), label="order = %d" % order)

            m.plot([0, COEF_CUT_FREQ*cut2*nyq], [sqrt(0.5), sqrt(0.5)],
                     '--', label='sqrt(0.5)')
            m.xlabel('f[Hz]')
            m.ylabel('Gain')
            m.grid(True)
            m.legend(loc='best')
        else:
            b, a = butter(order, cut1, btype='low')
            m.figure()

            order = 5
            c, d = butter(order, cut1, str(self._type))
            w, h = freqz(c, d, worN=2000)
            m.plot((fs * 0.5 / pi) * w, abs(h), label="order = %d" % order)

            m.plot([0, COEF_CUT_FREQ*cut1*nyq], [sqrt(0.5), sqrt(0.5)],
                     '--', label='sqrt(0.5)')
            m.xlabel('f[Hz]')
            m.ylabel('Gain')
            m.grid(True)
            m.legend(loc='best')

        return b, a

    def run(self):
        if self._name == 'Low Pass Filter 1':
            self._out_sig = self.butter_filter(self._input._out_sig, self._generator._fs,
                                   COEF_CUT_FREQ*self._generator._fm,
                                   0)
            self._out_sig = self._out_sig/max(abs(self._out_sig))*self._generator._am
        else:
            self._out_sig = self.butter_filter(self._input._out_sig, self._generator._fs,
                                               self._generator._fc-COEF_CUT_FREQ*self._generator._fm,
                                               self._generator._fc+COEF_CUT_FREQ*self._generator._fm)


# --------------------------- DEMODULATOR ----------------------------------


class Demodulator(Dev):

    def run(self):
        for s, t in zip(self._input._out_sig, self._generator._carr_sig): self._out_sig.append(s*t)


# --------------------------- AMPLIFIER  -----------------------------------


class Amplifier(Dev):

    def run(self):
        self._out_sig = self._input._out_sig/max(self._input._out_sig)*self._generator._am




__author__ = 'Gosia'
