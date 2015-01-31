__author__ = 'Gosia'


from classes import Generator
from classes import Modulator
from classes import SpectrumAnalyzer
from classes import Plotter
from classes import Channel
from classes import Filter
from classes import Demodulator
from classes import Amplifier
import matplotlib.pylab as m

gen = Generator("Generator")
mod = Modulator("Modulator")
spec = SpectrumAnalyzer("Spectrum Analyzer")
plot = Plotter("Plotter")
chan = Channel("Channel")
bpf = Filter("Band Pass Filter", "band")
demod = Demodulator("Demodulator")
lpf = Filter("Low Pass Filter", "low")
amp = Amplifier("Amplifier")

mod.set_gen(gen)
spec.set_gen(gen)
plot.set_gen(gen)
chan.set_gen(gen)
bpf.set_gen(gen)
demod.set_gen(gen)
lpf.set_gen(gen)
amp.set_gen(gen)
mod.connect(chan)
chan.connect(bpf)
bpf.connect(demod)
# chan.connect(demod)
demod.connect(lpf)
lpf.connect(amp)
# gen.notify(spec)
mod.notify(spec)
mod.notify(plot)
chan.notify(spec)
chan.notify(plot)
bpf.notify(spec)
bpf.notify(plot)
lpf.notify(spec)
lpf.notify(plot)
amp.notify(plot)



gen.input_data()

gen.run()
mod.run()
chan.run()
bpf.run()
demod.run()
lpf.run()
amp.run()
plot.run()
spec.run()





m.show()