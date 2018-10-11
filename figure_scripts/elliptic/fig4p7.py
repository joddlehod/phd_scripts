import sys
sys.path.append('..\\..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle


from phd_scripts.utility_scripts import pralines_wing_cla
from phd_scripts.utility_scripts import panair_wing_cla
from phd_scripts.utility_scripts import machup_wing_cla
# Aspect ratios to consider
RA = [8.0, 2.0, 0.5]

# Use lift slope from thin airfoil theory
a0 = 2.0 * np.pi

# Average chord length
c = 10.0

sec_cl_panair = []
sec_cl_pralines_classical = []
sec_cl_pralines_modifiedslender = []
sec_cl_pralines_hodson = []
for A in RA:
    sec_cl_panair.append(panair_wing_cla.sec_cl(c, A))
    sec_cl_pralines_classical.append(pralines_wing_cla.sec_cl(A, lowra='Classical'))
    sec_cl_pralines_modifiedslender.append(pralines_wing_cla.sec_cl(A, lowra='ModifiedSlender'))
    sec_cl_pralines_hodson.append(pralines_wing_cla.sec_cl(A, lowra='Hodson'))
    
# Set up a new plot
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4
plt.figure(figsize = (6.0, 4.0))
lw = 0.5  # Line width

# Plot the results
lines = cycle([(0, ()), (0, (5,5)), (0, (1,1)), (0, (3,5,1,5))])
for i, A in enumerate(RA):
    line = next(lines)
    markers = cycle(['s', '^', 'D', 'o'])
    plt.plot(sec_cl_pralines_classical[i][0], sec_cl_pralines_classical[i][1],
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_pralines_modifiedslender[i][0], sec_cl_pralines_modifiedslender[i][1],
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_pralines_hodson[i][0], sec_cl_pralines_hodson[i][1],
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_panair[i][0], sec_cl_panair[i][1],
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'full', markevery = 0.05)

markers = cycle(['s', '^', 'D', 'o'])
p1, = plt.plot([], [], label='Classical lifting line theory', linestyle = 'none',
        color = 'k', marker = next(markers), fillstyle = 'none')
p2, = plt.plot([], [], label='Modified slender wing line theory', linestyle = 'none',
        color = 'k', marker = next(markers), fillstyle = 'none')
p3, = plt.plot([], [], label='Hodson', linestyle = 'none',
        color = 'k', marker = next(markers), fillstyle = 'none')
p4, = plt.plot([], [], label='Vortex panel method', linestyle = 'none',
        color = 'k', marker = next(markers), fillstyle = 'full')

lines = cycle([(0, ()), (0, (5,5)), (0, (1,1)), (0, (3,5,1,5))])
p5 = plt.plot([], [], label='$A = 8$',
        color = 'k', linewidth = lw, linestyle = next(lines))
p6 = plt.plot([], [], label='$A = 2$',
        color = 'k', linewidth = lw, linestyle = next(lines))
p7 = plt.plot([], [], label='$A = 0.5$',
        color = 'k', linewidth = lw, linestyle = next(lines))
        
plt.legend(loc = 'upper right', prop={'size':8}, ncol = 2, framealpha = 1.0, numpoints = 1)

plt.xlabel(r'$y/b$')
plt.ylabel(r'$c_l$')#, rotation = 0, fontsize = 20)
plt.tight_layout()
plt.xlim(0, 0.5)
plt.ylim(0.0, 0.12)
plt.show()
