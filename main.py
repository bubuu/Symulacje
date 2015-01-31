__author__ = 'Gosia'


from classes import Generator
from classes import Modulator
from classes import SpectrumAnalyzer
from classes import Plotter
from classes import Channel
from classes import Filter
import matplotlib.pylab as m

gen = Generator("Generator")
mod = Modulator("Modulator")
spec = SpectrumAnalyzer("SpectrumAnalyzer")
plot = Plotter("Plotter")
chan = Channel("Channel")
bpf = Filter("BandPassFilter", "band")

mod.set_gen(gen)
spec.set_gen(gen)
plot.set_gen(gen)
chan.set_gen(gen)
bpf.set_gen(gen)
mod.connect(chan)
chan.connect(bpf)
mod.notify(spec)
mod.notify(plot)
chan.notify(spec)
chan.notify(plot)
bpf.notify(spec)
bpf.notify(plot)


gen.input_data()

gen.run()
mod.run()
chan.run()
bpf.run()
plot.run()
spec.run()




m.show()