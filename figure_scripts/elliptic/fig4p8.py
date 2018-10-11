import sys
sys.path.append('..\\..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import pralines_wing_cla
from phd_scripts.utility_scripts import panair_wing_cla
from phd_scripts.utility_scripts import machup_wing_cla
from phd_scripts.utility_scripts import wing


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
    sec_cl_panair.append(panair_wing_cla.sec_cl(c, A, viz=True))
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
    plt.plot(sec_cl_pralines_classical[i][0], np.asarray(sec_cl_pralines_classical[i][1]) * np.asarray(sec_cl_pralines_classical[i][2]),
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_pralines_modifiedslender[i][0], np.asarray(sec_cl_pralines_modifiedslender[i][1]) * np.asarray(sec_cl_pralines_modifiedslender[i][2]),
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_pralines_hodson[i][0], np.asarray(sec_cl_pralines_hodson[i][1]) * np.asarray(sec_cl_pralines_hodson[i][2]),
            color = 'k', linewidth = lw, linestyle = line,
            marker = next(markers), fillstyle = 'none', markevery = 0.05)
    plt.plot(sec_cl_panair[i][0], np.asarray(sec_cl_panair[i][1]) * np.asarray(sec_cl_panair[i][2]) / 10.0,
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
        
handles1 = [p1, p2, p3, p4]
labels1 = ['Classical lifting line theory', 'Modified slender wing line theory', 'Hodson', 'Vortex panel method']
l1 = plt.legend(handles1, labels1, loc = 'upper right', prop={'size':8}, ncol = 1, framealpha = 1.0, numpoints = 1)

handles2 = [p5[0], p6[0], p7[0]]
labels2 = [r'$A = 8$', r'$A = 2$', r'$A = 0.5$']
l2 = plt.legend(handles2, labels2, loc = (0.83, 0.6), prop={'size':8}, ncol = 1, framealpha = 1.0, numpoints = 1)
plt.gca().add_artist(l1)
plt.gca().add_artist(l2)

plt.xlabel(r'$y/b$')
plt.ylabel(r'$c_l (c/\overline{c})$')#, rotation = 0, fontsize = 20)
plt.tight_layout()
plt.xlim(0, 0.5)
plt.ylim(0.0, 0.12)

switch = [0.295, 0.26, 0.35]
for i in range(3):
    ra = RA[i]
    if ra == 'Circular': ra = 4.0 / np.pi
    inboard_wing_cl_hodson = 0.0
    outboard_wing_cl_hodson = 0.0
    y = sec_cl_pralines_hodson[i][0]
    cl = sec_cl_pralines_hodson[i][1]
    c = sec_cl_pralines_hodson[i][2]
    for y1, y2, cl1, cl2, c1, c2 in zip(y[:-1], y[1:], cl[:-1], cl[1:], c[:-1], c[1:]):
        sec_cl = 0.5 * (cl1 * c1 + cl2 * c2) * (y2 - y1)
        if y2 <= 0.0:
            continue
        if y2 < switch[i]:
            inboard_wing_cl_hodson += sec_cl
        else:
            outboard_wing_cl_hodson += sec_cl
            
    inboard_wing_cl_panair = 0.0
    outboard_wing_cl_panair = 0.0
    y = sec_cl_panair[i][0]        
    cl = sec_cl_panair[i][1]
    w = wing.Elliptic(ra, ra, 20)
    for y1, y2, cl1, c1 in zip(w.y[:-1]/ra, w.y[1:]/ra, cl, w.cc):
        sec_cl = cl1 * c1 * (y2 - y1)
        if y2 <= 0.0:
            continue
        if y2 < switch[i]:
            inboard_wing_cl_panair += sec_cl
        else:
            outboard_wing_cl_panair += sec_cl
    
    diff = inboard_wing_cl_panair - inboard_wing_cl_hodson
    total = panair_wing_cla.cla(10.0, 9.0) * np.radians(1.0)
    pct_diff = diff / total * 100
    print ("RA={:7.4f}, shift = {:7.4f}%".format(ra, pct_diff))

plt.show()

