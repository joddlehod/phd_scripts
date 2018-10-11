import sys
sys.path.append('..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import wing_cla
from phd_scripts.utility_scripts import pralines_wing_cla
from phd_scripts.utility_scripts import panair_wing_cla
from phd_scripts.utility_scripts import machup_wing_cla

# Use lift slope from thin airfoil theory
a0 = 2.0 * np.pi

# Average chord length
c_panair = 10.0

# Calculate the lift slope using Pralines
A_analytical = np.linspace(0.01, 8, 800)
A_numerical = np.linspace(0.1, 8, 80)
A_vortexpanel = np.linspace(1, 8, 8)
a_panair = [panair_wing_cla.cla(c_panair, x) for x in A_vortexpanel]
a_classical = wing_cla.a_classical(A_analytical, a0)
a_modified_slender = wing_cla.a_modified_slender(A_analytical, a0)
a_hodson = wing_cla.a_hodson(A_analytical, a0)

a_machup_classical = [machup_wing_cla.cla(x, lowra_method='Classical') for x in A_numerical]
a_machup_modified_slender = [machup_wing_cla.cla(x, lowra_method='ModifiedSlender') for x in A_numerical]
a_machup_hodson = [machup_wing_cla.cla(x, lowra_method='Hodson') for x in A_numerical]

# Define cycles for line patterns and markers
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
markers = cycle(['o', 's', '^', 'D', 'v'])
lw = 0.5  # Line width

# Set up a new plot
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4
plt.figure(figsize = (6.0, 3.667))

# Plot the analytical relations
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
plt.plot([], [], label = r'$Analytical$ $Solutions$', linestyle='none')
plt.plot(A_analytical, a_classical, label = "Classical lifting line theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot(A_analytical, a_modified_slender, label = "Modified slender wing theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot(A_analytical, a_hodson, label = "Hodson",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot([], [], label = ' ', linestyle='none')
plt.plot([], [], label = r'$Numerical$ $Solutions$', linestyle='none')
plt.plot(A_numerical, a_machup_classical, label = "Classical lifting line theory",
        color = 'k', linestyle = 'none',
        marker = 's', fillstyle = 'none', markevery = 0.05)
plt.plot(A_numerical, a_machup_modified_slender, label = "Modified slender wing theory",
        color = 'k', linestyle = 'none',
        marker = '^', fillstyle = 'none', markevery = 0.05)
plt.plot(A_numerical, a_machup_hodson, label = "Hodson",
        color = 'k', linestyle = 'none',
        marker = 'D', fillstyle = 'none', markevery = 0.05)
plt.plot(A_vortexpanel, a_panair, label = "Vortex panel method",
        color = 'k', linestyle = 'none',
        marker = 'o', fillstyle = 'full')

plt.legend(loc = 'lower right', prop={'size': 8}, ncol = 2,
        framealpha = 1.0, numpoints = 1)
plt.xlabel(r'$A$')
plt.ylabel(r'$a$')#, rotation = 0, fontsize = 12)

plt.tight_layout()
plt.xlim(0, 8)
plt.ylim(0, 5)
plt.show()
