__author__ = 'Gosia'

import classes as dev
from classes import Generator
from classes import Modulator
from classes import SpectrumAnalyzer
import matplotlib.pylab as m


mod = Modulator("Modulator")
spec = SpectrumAnalyzer("SpectrumAnalyzer")

dev.gen.connect(mod)
dev.gen.notify(spec)
mod.notify(spec)


dev.gen.input_data()

dev.gen.run()
mod.run()
spec.run()

m.show()