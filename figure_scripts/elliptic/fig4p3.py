import sys
sys.path.append('..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import wing_cla
from phd_scripts.utility_scripts import panair_wing_cla


# Use lift slope from thin airfoil theory
a0 = 2.0 * np.pi

# Define the array of aspect ratios
A = np.linspace(0.01, 8.0, 800)

# Calculate the lift slope using classical lifting line theory
a_classical = wing_cla.a_classical(A, a0)

# Calculate the lift slope using slender wing theory
a_slender = wing_cla.a_slender(A)

# Calculate the lift slope using modified slender wing theory
a_modified_slender = wing_cla.a_modified_slender(A)

# Calculate the lift slope using Helmbold's equation
a_helmbold = wing_cla.a_helmbold(A)

# Calculate the lift slope using Jones' equation
a_jones = [wing_cla.a_jones(x) for x in A]

# Calculate the lift slope using van Dyke's equation
a_vandyke = wing_cla.a_vandyke(A)

# Calculate the lift slope using Germain's equation
a_germain = wing_cla.a_germain(A)

# Calculate the lift slope using Hauptman and Miloh's equation
a_hauptmanmiloh = [wing_cla.a_hauptmanmiloh(x) for x in A]

# Calculate the lift slope using Kuchemann's equation
a_kuchemann = wing_cla.a_kuchemann(A)

# Calculate the lift slope using my proposed equation
a_hodson = wing_cla.a_hodson(A)


# Break up van Dyke results because of asymptote
a_vandyke_1 = [a for a in a_vandyke if a < 0]
A_vandyke_1 = A[:len(a_vandyke_1)]
a_vandyke_2 = a_vandyke[len(a_vandyke_1):]
A_vandyke_2 = A[len(a_vandyke_1):]

# Get numerical lifting surface results
krienes = wing_cla.a_krienes()
kinner = wing_cla.a_kinner()
jordan = wing_cla.a_jordan()
medan = wing_cla.a_medan()

# Get Panair results
#A_panair = np.concatenate((np.linspace(0.25, 2.0, 8), np.linspace(2.5, 3.0, 2),
#        np.linspace(4.0, 5.0, 2), np.linspace(6.0, 10.0, 3)))
A_panair = np.linspace(1.0, 8.0, 8)
c_panair = 10.0
cla_panair = [panair_wing_cla.cla(c_panair, x) for x in A_panair]

# Define cycles for line patterns and markers
#lines = cycle([(0, ()), (0, (1,1)), (0, (10,10)), (0, (3,10,1,10)), (0, (10,10,5,10)), (0, (3,10,1,10,1,10)), (0, (5,10)), (0, (15,5,1,5,5,5,1,5)), (0, (1,5))])
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
markers = cycle(['o', 's', '^', 'D', 'v'])
lw = 0.5  # Line width

# Set up a new plot
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4
plt.figure(figsize = (6.0, 4.0))

# Plot the analytical relations
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
plt.plot(A, a_classical, label = "Classical lifting line theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot(A, a_slender, label = "Slender wing theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot(A, a_modified_slender, label = "Modified slender wing theory",
        color = 'k', linewidth = lw, linestyle = next(lines))
plt.plot([], [], label = ' ', color = 'w')
plt.plot([], [], label = ' ', color = 'w')
        
# Plot the empirical relations
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
markers = cycle(['o', 's', '^', 'D', 'v'])
plt.plot(A, a_helmbold, label = "Helmbold",
        color = 'k', linewidth = lw, linestyle = next(lines),
        marker = next(markers), fillstyle = 'none', markevery = (0.000, 0.1))
#plt.plot(A, a_jones, label = "Jones",
#        color = 'k', linewidth = lw, linestyle = next(lines),
#        marker = next(markers), fillstyle = 'none', markevery = (0.015, 0.1))
#plt.plot(h2_vandyke_1, a_vandyke_1, label = "Van Dyke (1964)",
#        color = 'k', linewidth = lw, linestyle = next(lines))
#plt.plot(A_vandyke_2, a_vandyke_2, label = "Van Dyke",
#        color = 'k', linewidth = lw, linestyle = next(lines),
#        marker = next(markers), fillstyle = 'none', markevery = (0.03, 0.1))
#plt.plot(A, a_germain, label = "Germain",
#        color = 'k', linewidth = lw, linestyle = next(lines),
#        marker = next(markers), fillstyle = 'none', markevery = (0.045, 0.1))
plt.plot(A, a_kuchemann, label = r"K$\ddot{\rm{u}}$chemann",
        color = 'k', linewidth = lw, linestyle = next(lines),
        marker = next(markers), fillstyle = 'none', markevery = (0.050, 0.1))
plt.plot(A, a_hauptmanmiloh, label = "Hauptman & Miloh",
        color = 'k', linewidth = lw, linestyle = next(lines),
        marker = next(markers), fillstyle = 'none', markevery = (0.025, 0.1))
plt.plot(A, a_hodson, label = "Hodson",
        color = 'k', linewidth = lw, linestyle = next(lines),
        marker = next(markers), fillstyle = 'none', markevery = (0.075, 0.1))
plt.plot([], [], label = ' ', color = 'w')
        
# Plot the vortex panel and numerical lifting surface results
markers = cycle(['o', 's', '^', 'D', 'v'])
plt.plot(A_panair, cla_panair, label = "Vortex panel",
       color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
plt.plot(kinner[0], kinner[2], label = "Kinner (1937)",
        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
plt.plot(krienes[0], krienes[2], label = "Krienes (1941)",
        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
plt.plot(jordan[0], jordan[2], label = "Jordan (1974)",
        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')
plt.plot(medan[0], medan[2], label = "Medan (1974)",
        color = 'k', linestyle = 'none', marker = next(markers), fillstyle = 'full')

plt.legend(loc = 'lower right', prop={'size': 8}, ncol = 3,
        framealpha = 1.0, numpoints = 1)

plt.xlabel(r'$A$')
plt.ylabel(r'$a$')
plt.xlim(0, 8)
plt.ylim(0, 5.5)

plt.tight_layout()
plt.show()