import numpy as np
import os
import shutil
import time
import re
import glob
import matplotlib.pyplot as plt

import phd_scripts
from phd_scripts.utility_scripts import richardson_extrapolation


# Set up global plot parameters
plt.rc('font', **{'family':'serif', 'serif':['Times New Roman']})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 10
plt.rcParams["lines.markersize"] = 4


class Panair(object):
    """Wrapper class for creating, running, and post-processing Panair panel code analyses
    """
    def __init__(self, airfoil, wing, input_file,
            cmd = 'panair.exe', cmddir = None, jobdir = None):
        """Constructor
        """
        self.airfoil = airfoil
        self.wing = wing
        self.input_file = input_file
        
        self.cmd = cmd
        self.cmddir = cmddir if cmddir is not None else (
                phd_scripts.__path__[0] + os.sep + 'executables')
                
        self.jobdir = jobdir if jobdir is not None else self.name
        
        self._distributions = None
        self._sec_y = None
        self._sec_c = None
        self._sec_CL = None
        
        
    def setup(self, overwrite = None):
        # Make sure the input file exists
        if not os.path.isfile(self.input_file):
            print("Specified input file does not exist: " + self.input_file)
            return True
            
        # Create the job directory
        if os.path.isdir(self.jobdir):
            if overwrite is None:
                print("Directory already exists: " + self.jobdir)
                ow = input("Do you want to overwrite? (Y/n)\n")
                if len(ow) > 0 and (ow == 'n' or ow == 'N'):
                    overwrite = False
                else:
                    overwrite = True
                    
            if overwrite:
                shutil.rmtree(self.jobdir)
                time.sleep(1.0) # Give the file system some time...
            else:
                return False
        
        # Create the new job directory
        os.mkdir(self.jobdir)
        time.sleep(1.0) # Give the file system some time...
        
        # Copy the executable into the job directory
        shutil.copyfile(self.cmddir + os.sep + self.cmd,
                self.jobdir + os.sep + self.cmd)
        
        # Copy the input file into the job directory
        input_file_new = self.name + '.panair'
        shutil.copyfile(self.input_file, self.jobdir + os.sep + input_file_new)
        
        # Create an input file to pipe into the execution command
        with open(self.jobdir + os.sep + 'pipe', 'w') as pipe_file:
            pipe_file.write(input_file_new + '\n')

        return True
    
    
    def execute(self):
        """Execute the Panair analysis
        """
        # Move into the job directory
        cwd = os.getcwd()
        os.chdir(self.jobdir)
        
        # Execute Panair
        os.system(self.cmd + " < pipe > panair_stdout")
        [os.remove(file) for file in glob.glob('rwms*')]
        [os.remove(file) for file in glob.glob('ft*')]

        # Return to the original work directory
        os.chdir(cwd)
        
        
    @property
    def distributions(self):
        if self._distributions is None:
            resfilename = self.jobdir + os.sep + 'agps'
            if not os.path.isfile(resfilename):
                print("Panair output file '{}' does not exist!".format(resfilename))
                return None
                
            with open(resfilename, 'r') as resfile:
                lines = resfile.readlines()
                
            network = None
            column = None
            self._distributions = []
            dist1 = []
            dist2 = []
            for line in lines[6:]:
                if re.match('n[0-9]*c[0-9]*', line) is not None:
                    network = int(line[1:3])
                    if network == 3 or network == 6: continue  # Don't parse the wake network
                    
                    column = int(line[4:7])
                    if (network < 3 and column <= len(dist1)):
                        table = dist1[column - 1]  # Append to existing table (wing 1)
                    elif (network > 3 and column <= len(dist2)):
                        table = dist2[column - 1]  # Append to existing table (wing 2)
                    else:
                        table = {'x': [], 'y': [], 'z': [], 'cp': []}  # Create new table
                    
                elif re.match('\*eof', line) is not None:
                    if column is not None:
                        if network < 3 and column > len(dist1):
                            dist1.append(table)
                        elif network > 3 and column > len(dist2):
                            dist2.append(table)
                    table = None
                    network = None
                    column = None
                    
                elif re.match(' irow', line) is not None:
                    pass
                    
                elif table is not None:
                    data = line.split()
                    table['x'].append(float(data[1]))
                    table['y'].append(float(data[2]))
                    table['z'].append(float(data[3]))
                    table['cp'].append(float(data[4]))
    
            if self.wing.symm: self._distributions = dist1
            else: self._distributions = np.concatenate((dist2[:-1:], dist1[:]))
        return self._distributions


    @property
    def sec_CL(self):
        """Get the section lift distribution by integrating pressure over each wing section
        
        Note: Values are interpolated to section theta-midpoints
        """
        if self._sec_CL is None:
            secCL = np.asarray([integrate(dist['cp'], dist['x'])
                    for dist in self.distributions])
            self._sec_CL = interpolate(self.wing.y[:-1], self.wing.y[1:],
                    secCL[:-1], secCL[1:], self.wing.yc) / self.sec_c
                
        return self._sec_CL


    @property
    def sec_y(self):
        """Get the section y-coordinates from the distribution table
        
        Note: Values are interpolated to section theta-midpoints
        """
        if self._sec_y is None:
            secY = np.asarray([dist['y'][0] for dist in self.distributions])
            self._sec_y = interpolate(self.wing.y[:-1], self.wing.y[1:],
                    secY[:-1], secY[1:], self.wing.yc)
            
        return self._sec_y
    
    
    @property
    def sec_c(self):
        """Get the section chord distribution
        
        Note: Values are interpolated to section theta-midpoints
        """
        if self._sec_c is None:
            secC = np.asarray([max(dist['x']) - min(dist['x']) for dist in self.distributions])
            self._sec_c = interpolate(self.wing.y[:-1], self.wing.y[1:],
                    secC[:-1], secC[1:], self.wing.yc)
                
        return self._sec_c
        
        
    @property
    def CL(self):
        """Get the wing lift coefficient by integrating sec_CL over the wingspan
        
        Note: This function assumes the section data is for a single semispan while
              the wing area is the total for both semispans
        """
        cl = sum(self.sec_CL * self.wing.sec_Area) / self.wing.Area
        if self.wing.symm: return 2.0 * cl
        else: return cl

        
    @property
    def name(self):
        return "panair_{}_{}".format(self.airfoil.name, self.wing.name)
        
        
    def plot_sec_CL(self):
        plt.figure(figsize=(6.0, 5.0))
        plt.plot(self.wing.yc / b, self.sec_CL, color='k', linestyle=(0, (None, None)),
                marker='o', fillstyle='none', markersize=6)
                
        plt.xlabel(r'$y/b$')
        plt.ylabel(r'$c_l$')
        plt.xlim(0.0, 0.5)
        plt.ylim(0.0, 1.1 * max(self.sec_CL))
        plt.legend(loc='lower left')
        plt.tight_layout()
        plt.show()
        
        
def extrapolate_CL(panair1, panair2, panair3):
    """Extrapolate CL values based on three grid refinements
    
    This function extrapolates spanwise section lift coefficients using
    Richardson extrapolation on results from three Panair panel code
    simulations with successively-refined meshes. It is assumed that each
    successive mesh refinement doubles the number of spanwise sections
    over the previous grid.
    
    panair1 = coarse-mesh analysis
    panair2 = medium-mesh analysis
    panair3 = fine-mesh analysis
    """
    clp1 = panair1.sec_CL
    
    clp2 = np.asarray([(cl1 * a1 + cl2 * a2) / (a1 + a2) for a1, a2, cl1, cl2 in
            zip(panair2.wing.sec_Area[:-1:2], panair2.wing.sec_Area[1::2],
            panair2.sec_CL[:-1:2], panair2.sec_CL[1::2])])
    
    clp3 = np.asarray([(cl1 * a1 + cl2 * a2 + cl3 * a3 + cl4 * a4) / (a1 + a2 + a3 + a4)
            for a1, a2, a3, a4, cl1, cl2, cl3, cl4 in zip(
            panair3.wing.sec_Area[:-3:4], panair3.wing.sec_Area[1:-2:4],
            panair3.wing.sec_Area[2:-1:4], panair3.wing.sec_Area[3::4],
            panair3.sec_CL[:-3:4], panair3.sec_CL[1:-2:4],
            panair3.sec_CL[2:-1:4], panair3.sec_CL[3::4])])
    
    (cl_extrapolated, order) = richardson_extrapolation.extrapolate(1, 2, 4, clp1, clp2, clp3)
    y_extrapolated = panair1.sec_y
    return (y_extrapolated, cl_extrapolated)


def integrate(f, x):
    """Integrate a function over a variable using the trapezoidal rule
    
    f = List/array of function values
    x = List/array of corresponding independent variable values
    """
    int_f = 0.0
    for f1, f2, x1, x2 in zip(f[:-1], f[1:], x[:-1], x[1:]):
        int_f += 0.5 * (f1 + f2) * (x2 - x1)
        
    return int_f
    
    
def interpolate(x1, x2, f1, f2, x):
    """Interpolate a function to a given x
    """
    try:
        return (x - x1) / (x2 - x1) * (f2 - f1) + f1
    except:
        print("Could not interpolate between {} and {}".format(x1, x2))
        return None