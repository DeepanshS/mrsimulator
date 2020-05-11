#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wollastonite
^^^^^^^^^^^^

29Si (I=1/2) spinning sideband simulation.
"""
#%%
# Wollastonite is a high-temperature calcium-silicate,
# :math:`\beta−\text{Ca}_3\text{Si}_3\text{O}_9`,
# with three distinct :math:`^{29}\text{Si}` sites. The :math:`^{29}\text{Si}`
# tensor parameters
# were obtained from Hansen et. al. [#f1]_
import matplotlib.pyplot as plt
from mrsimulator import Isotopomer
from mrsimulator import Simulator
from mrsimulator import Site

#%%
# **Step 1** Create sites.

S29_1 = Site(
    isotope="29Si",
    isotropic_chemical_shift=-89.0,
    shielding_symmetric={"zeta": 59.8, "eta": 0.62},
)
S29_2 = Site(
    isotope="29Si",
    isotropic_chemical_shift=-89.5,
    shielding_symmetric={"zeta": 52.1, "eta": 0.68},
)
S29_3 = Site(
    isotope="29Si",
    isotropic_chemical_shift=-87.8,
    shielding_symmetric={"zeta": 69.4, "eta": 0.60},
)

sites = [S29_1, S29_2, S29_3]

#%%
# **Step 2** Create isotopomers from these sites.

isotopomers = [Isotopomer(sites=[site]) for site in sites]

#%%
# **Step 3** Create a Bloch decay spectrum method.

from mrsimulator.methods import BlochDecaySpectrum

method = BlochDecaySpectrum(
    channels=["29Si"],
    magnetic_flux_density=14.1,
    rotor_frequency=1500,
    dimensions=[{"count": 2046, "spectral_width": 25000, "reference_offset": -10000}],
)


#%%
# **Step 4** Create the Simulator object and add method and isotopomer objects.

sim_wollastonite = Simulator()

# add isotopomers
sim_wollastonite.isotopomers += isotopomers

# add method
sim_wollastonite.methods += [method]

#%%
# **Step 5** Simulate the spectrum.

sim_wollastonite.run()
sim_wollastonite.methods[0].simulation.dimensions[0].to("ppm", "nmr_frequency_ratio")
x, y = sim_wollastonite.methods[0].simulation.to_list()

#%%
# **Step 6** Plot.

plt.figure(figsize=(4, 3))
plt.plot(x, y, color="black", linewidth=1)
plt.xlabel("frequency / ppm")
plt.xlim(x.value.max(), x.value.min())
plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.5)
plt.tight_layout()
plt.show()

#%%
# .. [#f1] Hansen, M. R., Jakobsen, H. J., Skibsted, J., :math:`^{29}\text{Si}`
#       Chemical Shift Anisotropies in Calcium Silicates from High-Field
#       :math:`^{29}\text{Si}` MAS NMR Spectroscopy, Inorg. Chem. 2003,
#       **42**, *7*, 2368-2377.
#       `DOI: 10.1021/ic020647f <https://doi.org/10.1021/ic020647f>`_
