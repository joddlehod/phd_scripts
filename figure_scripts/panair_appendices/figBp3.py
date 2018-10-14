import sys
sys.path.append('..\\..\\..\\')

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from phd_scripts.utility_scripts import panair_wing_cla

# Set up global plot parameters
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4


# Define the wing
A = 4  # Aspect ratio
c_avg = 10  # Average chord

# Plot the grid-convergence data
panair_wing_cla.sec_cl(c_avg, A, None, False, True, True)