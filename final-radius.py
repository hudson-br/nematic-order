import os
import numpy as np
import matplotlib.pyplot as plt
import configreader


path = '/Users/morpho/TURLIERLAB Dropbox/Hudson Rocha/Postdoc/filament-orientation/data/correlation-length'
os.chdir(path)
cwd = os.getcwd()

print(cwd)

contractility = []
radius = [] 
time = []
for elem in os.listdir(cwd):
    if elem.startswith("run"):
        try:
            print(elem)
            f = np.genfromtxt(elem+ '/output/data.csv', delimiter=';', unpack=True)
            radius = np.append(radius,f[2][-1])
            C = configreader.Config()
            config = C.read(elem+  "/config.conf")
            contractility = np.append(contractility, float(config["parameters"]["contractility_strength"]))
        except:
            pass

os.chdir(path)
cwd = os.getcwd()
plt.plot(contractility, radius,'.')
plt.xlabel('Contractility $\zeta/\zeta_0$')
plt.ylabel('Final furrow radius')
plt.savefig('furrow_radius.pdf')
plt.show()