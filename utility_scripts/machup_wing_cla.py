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


def _run_machup(RA, RT = None, solver = None, lowra_method = None,
        root_clustering = None, tip_clustering = None, viz = False):
    """Calculate the wing lift slope of a tapered wing using MachUp
    
    This function calculates the lift slope of a finite tapered wing using
    MachUp, an open-source tool based on the numerical lifting line method of
    Phillips and Snyder.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        RT = Taper ratio (ratio of tip chord to root chord), None = Elliptic wing
        solver = Solver to use ('linear' or 'nonlinear')
        lowra_method = Low-aspect-ratio method to use ('Classical', 'Kuchemann', 'Jones',
                'Hodson', 'Helmbold', 'Slender', 'ModifiedSlender')
        root_clustering = Use cosine-clustering at the root? (True/False)
        tip_clustering = Use cosine-clustering at the tip? (True/False)
        viz = Visualize the spanwise lift coefficient? True/False
    """
    # Define the grid discretization
    npts = 100

    # Determine the average chord length to use for best results
    c = 1.0

    # Calculate the wingspan
    if RA == 'Circular': b = 4.0 / np.pi * c
    else: b = RA * c
    
    # Create the airfoil and wing
    a = airfoil.FlatPlate()
    if RT is None:
        w = wing.Elliptic(RA, b, npts, symm=True)
    elif RT == 1.0:
        w = wing.Rectangular(RA, b, npts, symm=True)
    else:
        w = wing.Tapered(RA, RT, b, npts, symm=True)
    
    # Create the MachUp solver
    m = machup.MachUp(a, w)
    m.solver = solver
    m.lowra_method = lowra_method
    m.root_clustering = root_clustering
    m.tip_clustering = tip_clustering
    
    # Setup and execute
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
    
    
def sec_cl(RA, RT = None, solver = None, lowra_method = 'Classical',
        root_clustering = None, tip_clustering = None, viz = False):
    m = _run_machup(RA, RT, solver, lowra_method, root_clustering, tip_clustering, viz)
    return (m.sec_y / m.wing.b, m.sec_CL)
    
    
def cla(RA, RT = None, solver = None, lowra_method = 'Classical',
        root_clustering = None, tip_clustering = None, viz = False):
    m = _run_machup(RA, RT, solver, lowra_method, root_clustering, tip_clustering, viz)
    return m.CL / np.radians(1.0)
