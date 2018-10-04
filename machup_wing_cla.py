import airfoil
import wing
import machup
import panair
import richardson_extrapolation
import plot

import numpy as np


def sweep(AList):
    return [a_panair(A) for A in AList]


def a_machup(A, RT = None, viz = False):
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
    b = A * c
    
    # Define the angle of attack
    alpha = np.radians(1.0)
    
    # Define a set of markers to use for plotting
    markers = ['o', 's', '^']
    
    # Initialize lists for 
    ys = []
    cls = []

    a = airfoil.FlatPlate()
    if RT is None:
        w = wing.Elliptic(A, b, npts, symm=True, suffix='sqc')
    elif RT == 1.0:
        w = wing.Rectangular(A, b, npts, symm=True, suffix='sqc')
    else:
        w = wing.Tapered(A, RT, b, npts, symm=True, suffix='sqc')
    
    m = machup.MachUp(a, w, template = 'input_symm.json',
            cmd = 'MachUp.exe')
    if(m.setup(overwrite = False)):
        m.execute()
        
    # Plot the lift distribution
    if viz:
        plot.new(r'$y/b$', r'Section $C_L$', [0.0, 0.5], [0.0, 0.04], size=(5.0, 6.0))
        plot.add(m.sec_y, m.sec_CL, marker = markers[0])
        plot.draw('lower left')
        plot.show()
    
    # Calculate the total lift coefficient and the wing lift slope
    return m.CL / alpha
