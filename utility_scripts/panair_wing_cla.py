from phd_scripts.utility_scripts import airfoil
from phd_scripts.utility_scripts import wing
from phd_scripts.utility_scripts import machup
from phd_scripts.utility_scripts import panair
from phd_scripts.utility_scripts import richardson_extrapolation

import numpy as np
import matplotlib.pyplot as plt


# Set up global plot parameters
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4

            
def sec_cl(c, RA, RT = None, root_clustering = False, tip_clustering = True,
        viz = False, npts = [20, 40, 80], ts = [0.16, 0.08, 0.04]):
    """Calculate the wing lift slope of a finite wing using Panair
    
    This function calculates the wing lift slope of a finite wing using
    Panair, a high-order panel code developed at Boeing in the 1970s. The
    panel code is solved nine times, using three different grid sizes and
    three different airfoil thicknesses. The results are extrapolated using
    Richardson Extrapolation to approximate a thin airfoil on a refined grid.
    
    Inputs:
        c = Average chord length
        RA = Aspect ratio of wing (b^2 / Sw)
        RT = Taper ratio (ratio of tip chord to root chord)
        root_clustering = Use cosine-clustering at the root? (True/False)
        tip_clustering = Use cosine-clustering at the tip? (True/False)
        viz = Visualize the spanwise lift coefficient? True/False
        npts = Number of spanwise and chordwise sections
        ts = Thicknesses (fraction of chord)
    """
    # Calculate the wingspan
    if RA == 'Circular': b = 4.0 / np.pi * c
    else: b = RA * c
    
    # Define a set of markers to use for plotting
    markers = ['o', 's', '^']
    
    # Initialize lists for 
    ys = []
    cls = []
    for t in ts:
        res = []
        for npt in npts:
            a = airfoil.Joukowski(t, 0.0, npt)
            
            if RT is None:
                w = wing.Elliptic(RA, b, npt, symm=True, suffix=None,
                        root_clustering = root_clustering,
                        tip_clustering = tip_clustering)
            elif RT == 1.0:
                w = wing.Rectangular(RA, b, npt, symm=True, suffix=None,
                        root_clustering = root_clustering,
                        tip_clustering = tip_clustering)
            else:
                w = wing.Tapered(RA, RT, b, npt, symm=True, suffix=None,
                        root_clustering = root_clustering,
                        tip_clustering = tip_clustering)
            
            m = machup.MachUp(a, w)
            if(m.setup(overwrite = False)):
                m.execute()
        
            p = panair.Panair(a, w, m.panair_input_file)
            if(p.setup(overwrite = False)):
                p.execute()
            
            res.append(p)
            
        # Extrapolate grid-refinement results to a mesh of infinite panal count
        (y_ext, cl_ext) = panair.extrapolate_CL(res[0], res[1], res[2])
        
        # Plot the extrapolated lift distribution
        if viz:
            plt.figure(figsize = (4.0, 2.5))
            max_cl = 0.0
            for npt, p, m in zip(npts, res, markers):
                plt.plot(p.sec_y / b, p.sec_CL, label='{0} x {0}'.format(npt), color='k',
                        linestyle=(0, ()), marker=m, fillstyle='none', markevery=0.05)
                max_cl = max(max_cl, max(p.sec_CL))

            plt.plot(y_ext / b, cl_ext, label='Extrapolated', color='k',
                    linestyle=(0, ()), marker='x', fillstyle='none', markevery=0.05)
            max_cl = max(max_cl, max(cl_ext))
                    
            plt.xlabel(r'$y/b$')
            plt.ylabel(r'$c_l$')
            plt.xlim(0.0, 0.5)
            plt.ylim(0.0, 1.1 * max_cl)
            plt.legend(loc = 'lower left', prop={'size': 8}, ncol = 1,
                    framealpha = 1.0, numpoints = 1)
            plt.tight_layout()
            plt.show()
        
        # Add the mesh-extrapolated results to the list
        ys.append(y_ext / b)
        cls.append(cl_ext)
    
    # Extrapolate the mesh-extrapolated results to approximate an airfoil of
    # zero thickness
    (cl_ext, order) = richardson_extrapolation.extrapolate(ts[2], ts[1], ts[0], cls[0], cls[1], cls[2])

    # Plot the spanwise lift distribution for each mesh-extrapolated result
    if viz:
        # Plot the individual mesh-extrapolated results
        plt.figure(figsize = (4.0, 2.5))
        max_cl = 0.0
        for t, y, cl, m in zip(ts, ys, cls, markers):
            plt.plot(y, cl, label='t = {:.0F}%'.format(100 * t), color='k',
                    linestyle=(0, ()), marker=m, fillstyle='none')
            max_cl = max(max_cl, max(cl))

        # Plot the final extrapolated (t = 0, mesh = infinity) lift distribution
        plt.plot(ys[0], cl_ext, label='t = 0% (Extrapolated)', color='k',
                linestyle=(0, ()), marker='x', fillstyle='none')
        max_cl = max(max_cl, max(cl_ext))
                
        plt.xlabel(r'$y/b$')
        plt.ylabel(r'$c_l$')
        plt.xlim(0.0, 0.5)
        plt.ylim(0.0, 1.1 * max_cl)
        plt.legend(loc = 'lower left', prop={'size': 8}, ncol = 1,
                framealpha = 1.0, numpoints = 1)
        plt.tight_layout()
        plt.show()

    return (ys[0], cl_ext, res[0].sec_c)
    
    
def cla(c, RA, RT = None, root_clustering = False, tip_clustering = True,
        viz = False, npts = [20, 40, 80], ts = [0.16, 0.08, 0.04]):
    if RA == 'Circular': b = 4.0 / np.pi * c
    else: b = RA * c

    # Calculate the section lift distribution
    yb, cl_ext, c = sec_cl(c, RA, RT, root_clustering, tip_clustering, viz, npts, ts)
            
    # Calculate the total lift coefficient and the wing lift slope
    if RT is None:
        w = wing.Elliptic(RA, b, npts[0], symm=True, suffix=None,
                root_clustering = root_clustering, tip_clustering = tip_clustering)
    elif RT == 1.0:
        w = wing.Rectangular(RA, b, npts[0], symm=True, suffix=None,
                root_clustering = root_clustering, tip_clustering = tip_clustering)
    else:
        w = wing.Tapered(RA, RT, b, npts[0], symm=True, suffix=None,
                root_clustering = root_clustering, tip_clustering = tip_clustering)
        
    cl = np.sum(cl_ext * w.sec_Area) / np.sum(w.sec_Area)
    return cl / np.radians(1.0)
    
