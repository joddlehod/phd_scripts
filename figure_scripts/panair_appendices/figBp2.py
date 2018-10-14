import sys
sys.path.append('..\\..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import airfoil, wing, machup, panair

# Set up global plot parameters
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4


# Define the airfoil
t = 0.04  # Airfoil thickness
npts = 80  # Number of panels around the airfoil perimeter
cld = 0.0  # Design lift coefficient
a = airfoil.Joukowski(t, cld, npts)

# Define the wing parameters
A = 4.0  # Aspect ratio
cs = np.asarray([1, 2, 5, 10])  # Average chord
bs = A * cs  # Wingspan
nSec = npts  # Number of spanwise sections - same as airfoil panels

# Run the model for each average chord length
ps = []
for c, b in zip(cs, bs):
    # Create the wing
    b = A * c  # Wingspan
    w = wing.Elliptic(A, b, nSec)
    
    # Execute MachUp to generate a Panair input file
    m = machup.MachUp(a, w)
    if (m.setup(False)):
        m.execute()
    
    p = panair.Panair(a, w, m.panair_input_file)
    if (p.setup(False)):
        p.execute()
        
    ps.append(p)
        
plt.figure(figsize = (4.0, 2.5))
markers = cycle(['o', 's', '^', 'D', 'v'])
lines = cycle([(0, ()), (0, (1,1)), (0, (5,5)), (0, (3,5,1,5))])
for p, b, c in zip(ps, bs, cs):
    plt.plot(p.sec_y / b, p.sec_CL, color = 'k', label = r'$c={}$'.format(c),
            linestyle = next(lines), marker = next(markers),
            fillstyle = 'none', markevery=0.1)

plt.xlabel(r'$y/b$')
plt.ylabel(r'$c_l$')
plt.xlim(0, 0.5)
plt.ylim(0, 1.1 * max(ps[3].sec_CL))

plt.legend(loc = 'lower left', prop={'size': 8}, ncol = 1,
        framealpha = 1.0, numpoints = 1)
        
plt.tight_layout()
plt.show()
