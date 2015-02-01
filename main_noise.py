__author__ = 'Gosia'


from classes_noise import Generator
from classes_noise import Modulator
from classes_noise import SpectrumAnalyzer
from classes_noise import Plotter
from classes_noise import Channel
from classes_noise import Filter
from classes_noise import Demodulator
from classes_noise import Amplifier
import matplotlib.pylab as m

gen = Generator("Generator")
lpf1 = Filter("Low Pass Filter 1", "low")
mod = Modulator("Modulator")
spec = SpectrumAnalyzer("Spectrum Analyzer")
plot = Plotter("Plotter")
chan = Channel("Channel")
bpf = Filter("Band Pass Filter", "band")
demod = Demodulator("Demodulator")
lpf = Filter("Low Pass Filter", "low")
amp = Amplifier("Amplifier")

mod.set_gen(gen)
lpf1.set_gen(gen)
spec.set_gen(gen)
plot.set_gen(gen)
chan.set_gen(gen)
bpf.set_gen(gen)
demod.set_gen(gen)
lpf.set_gen(gen)
amp.set_gen(gen)
gen.connect(lpf1)
lpf1.connect(mod)
mod.connect(chan)
chan.connect(bpf)
bpf.connect(demod)
# chan.connect(demod)
demod.connect(lpf)
lpf.connect(amp)
# gen.notify(spec)
lpf1.notify(plot)
lpf1.notify(spec)
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
lpf1.run()
mod.run()
chan.run()
bpf.run()
demod.run()
lpf.run()
amp.run()
plot.run()
spec.run()





m.show()