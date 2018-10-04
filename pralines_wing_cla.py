import pralines
import wing
import richardson_extrapolation

import numpy as np


def sec_cl(A, a0 = 2.0 * np.pi, RT = None, lowra = 'Classical'):
    """Calculate the wing lift slope of a wing using Pralines
    
    This function calculates the lift distribution of a finite wing using
    Pralines, a numerical algorithm based on the classical lifting line
    theory of Prandtl. It approximates the solution to classical lifting
    line theory using a truncated Fourier series.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = Section lift slope
        RT = Taper ratio (ratio of tip chord to root chord) - None = Elliptic planform
        lowra = Low-aspect-ratio method ('Classical', 'Hodson', or 'ModifiedSlender')
    """
    # Define the grid discretization and airfoil thicknesses
    npts = 100

    # Define the average chord length
    c = 1.0

    # Calculate the wingspan
    if A == 'Circular': b = 4.0 / np.pi * c
    else: b = A * c

    # Create a wing object of the desired type
    if RT is None:
        w = wing.Elliptic(A, b, npts, symm=True, suffix=None)
    elif RT == 1.0:
        w = wing.Rectangular(A, b, npts, symm=True, suffix=None)
    else:
        w = wing.Tapered(A, RT, b, npts, symm=True, suffix=None)
    
    # Solve the problem using Pralines
    pr = pralines.Pralines(w, a0, lowra)
    if(pr.setup(overwrite = False)):
        pr.execute()
        
    wing_cl = pr.WingLiftCoefficient
    ys, cls = pr.sec_cl()
    return (ys, [wing_cl * cl for cl in cls])
    
    
def cla(RA, a0 = 2.0 * np.pi, RT = None, lowra = 'Classical'):
    ()
