from phd_scripts.utility_scripts import airfoil
from phd_scripts.utility_scripts import wing
from phd_scripts.utility_scripts import machup
from phd_scripts.utility_scripts import panair
from phd_scripts.utility_scripts import richardson_extrapolation

import matplotlib.pyplot as plt
import numpy as np


# Set up global plot parameters
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4


def _run_machup(RA, RT = None, viz = False):
    """Calculate the wing lift slope of a tapered wing using MachUp
    
    This function calculates the lift slope of a finite tapered wing using
    MachUp, an open-source tool based on the numerical lifting line method of
    Phillips and Snyder.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        RT = Taper ratio (ratio of tip chord to root chord), None = Elliptic wing
        viz = Visualize the spanwise lift coefficient? True/False
    """
    # Define the grid discretization
    npts = 100

    # Determine the average chord length to use for best results
    c = 1.0

    # Calculate the wingspan
    if RA == 'Circular': b = 4.0 / np.pi * c
    else: b = RA * c
    
    a = airfoil.FlatPlate()
    if RT is None:
        w = wing.Elliptic(RA, b, npts, symm=True)
    elif RT == 1.0:
        w = wing.Rectangular(RA, b, npts, symm=True)
    else:
        w = wing.Tapered(RA, RT, b, npts, symm=True)
    
    m = machup.MachUp(a, w)
    if(m.setup(overwrite = False)):
        m.execute()
        
    # Plot the lift distribution
    if viz:
        plt.figure(figsize=(6.0, 5.0))
        plt.plot(m.sec_y / b, m.sec_CL, color='k', linestyle=(0, (None, None)),
                marker='o', fillstyle='none', markersize=6)
                
        plt.xlabel(r'$y/b$')
        plt.ylabel(r'$c_l$')
        plt.xlim(0.0, 0.5)
        plt.ylim(0.0, 1.1 * max(m.sec_CL))
        plt.legend(loc='lower left')
        plt.tight_layout()
        plt.show()
        
    return m
    
    
def sec_cl(RA, RT = None, viz = False):
    m = _run_machup(RA, RT)
    return (m.sec_y / m.wing.b, m.sec_CL)
    
    
def cla(RA, RT = None, viz = False):
    m = _run_machup(RA, RT)
    return m.CL / np.radians(1.0)
