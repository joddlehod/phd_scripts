import sys
sys.path.append('..\\..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import wing
from phd_scripts.utility_scripts import pralines
from phd_scripts.utility_scripts import panair_wing_cla
from phd_scripts.utility_scripts import machup_wing_cla

# Use lift slope from thin airfoil theory
a0 = 2.0 * np.pi

# Define the array of taper ratios
RT = np.linspace(0.5, 1.0, 5)

# Define the array of aspect ratios
A = np.linspace(0.1, 8.0, 80)

# Calculate the lift slope using Pralines
rt = 1.0
a_classical = []
a_hodson = []
a_modified_slender = []
for aspect_ratio in A:
    w = wing.Rectangular(aspect_ratio, aspect_ratio, 100)
    pr_classical = pralines.Pralines(w, a0, 'Classical')
    if pr_classical.setup(overwrite = False):
        pr_classical.execute()
    a_classical.append(pr_classical.WingLiftSlope)
    
    pr_hodson = pralines.Pralines(w, a0, 'Hodson')
    if pr_hodson.setup(overwrite = False):
        pr_hodson.execute()
    a_hodson.append(pr_hodson.WingLiftSlope)
    
    pr_modified_slender = pralines.Pralines(w, a0, 'ModifiedSlender')
    if pr_modified_slender.setup(overwrite = False):
        pr_modified_slender.execute()
    a_modified_slender.append(pr_modified_slender.WingLiftSlope)
    
    
## Get numerical lifting surface results
#krienes = wing_cla.a_krienes()
#kinner = wing_cla.a_kinner()
#jordan = wing_cla.a_jordan()
#medan = wing_cla.a_medan()

# Get Panair results
#A_panair = np.concatenate((np.linspace(0.25, 2.0, 8), np.linspace(2.5, 3.0, 2),
#        np.linspace(4.0, 5.0, 2), np.linspace(6.0, 10.0, 3)))
A_panair = np.linspace(1.0, 8.0, 8)
c = 10.0
cla_panair = [panair_wing_cla.cla(c, x, rt, False) for x in A_panair]
#cla_machup = [machup_wing_cla_tapered.a_machup(x, rt, False) for x in A_panair]

# Define cycles for line patterns and markers
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
markers = cycle(['o', 's', '^', 'D', 'v'])
lw = 0.5  # Line width

# Set up a new plot
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4
plt.figure(figsize = (4.0, 2.5))

# Plot the analytical relations
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
plt.plot(A, a_classical, label = "Classical lifting line theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
#plt.plot(A, a_slender, label = "Slender wing theory",
#        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot(A, a_modified_slender, label = "Modified slender wing theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
#plt.plot([], [], label = ' ', color = 'w')
#plt.plot([], [], label = ' ', color = 'w')
        
# Plot the empirical relations
markers = cycle(['o', 's', '^', 'D', 'v'])
plt.plot(A, a_hodson, label = "Hodson",
        color = 'k', linewidth = lw, linestyle = next(lines))
#plt.plot([], [], label = ' ', color = 'w')
        
# Plot the numerical lifting surface results
#markers = cycle(['o', 's', '^', 'D', 'v'])
#plt.plot(kinner[0], kinner[2], label = "Kinner (1937)",
#        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
#plt.plot(krienes[0], krienes[2], label = "Krienes (1941)",
#        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
#plt.plot(jordan[0], jordan[2], label = "Jordan (1974)",
#        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
#plt.plot(medan[0], medan[2], label = "Medan (1974)",
#        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')

# Plot Panair and MachUp results
plt.plot(A_panair, cla_panair, label = "Vortex panel method",
       color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
#plt.plot(A_panair, cla_machup, label = "MachUp",
#       color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')

plt.legend(loc = 'lower right', prop={'size': 8}, ncol = 1,
        framealpha = 1.0, numpoints = 1)

plt.xlabel(r'$A$')
plt.ylabel(r'$a$  $(\mathrm{rad}^{-1})$')
plt.xlim(0, 8)
plt.ylim(0.0, 5.0)

plt.tight_layout()
plt.show()

pct_diff = [abs(ap - ah) / ap for ap, ah in zip(cla_panair, a_hodson[9::10])]
for p in pct_diff: print(p)
