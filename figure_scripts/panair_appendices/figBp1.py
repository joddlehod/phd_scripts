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
npts = 20  # Number of panels around the airfoil perimeter
cld = 0.0  # Design lift coefficient
a = airfoil.Joukowski(t, cld, npts)

# Define the wing
A = 4.0  # Aspect ratio
c_avg = 1.0  # Average chord
b = A  # Wingspan - A = b / c_avg
nSec = npts  # Number of spanwise sections - same as airfoil panels
w = wing.Elliptic(A, b, nSec)

# Execute MachUp to generate a Panair input file
m = machup.MachUp(a, w)
if (m.setup(True)):
    m.execute()

p = panair.Panair(a, w, m.panair_input_file)
if (p.setup(True)):
    p.execute()
    
plt.figure(figsize = (4.0, 2.5))
plt.plot(p.sec_y / b, p.sec_CL,
       color = 'k', linestyle = 'none', marker = 'o', fillstyle = 'full')

plt.xlabel(r'$y/b$')
plt.ylabel(r'$c_l$')
plt.xlim(0, 0.5)
plt.ylim(0, 1.1 * max(p.sec_CL))

plt.tight_layout()
plt.show()
