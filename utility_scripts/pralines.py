import numpy as np
import os
import shutil
import time

import phd_scripts
from phd_scripts.utility_scripts import airfoil
from phd_scripts.utility_scripts import wing


class Pralines(object):
    """Wrapper class for creating, running, and post-processing Pralines lifting line analyses
    """
    def __init__(self, wing, a0, larc, cmd = 'PrandtlsLiftingLine.exe',
            cmddir = None, jobdir = None):
        """Constructor
        """
        self.wing = wing  # Wing object
        self.a0 = a0  # Section lift slope
        self.larc = larc  # Low aspect ratio correction method
                          # Options are ('Classical', 'Hodson', 'ModifiedSlender')
                          
        self.cmd = cmd  # Execution command
        self.cmddir = cmddir if cmddir is not None else (
                phd_scripts.__path__[0] + os.sep + 'executables')
        self.cmddir = os.path.abspath(self.cmddir)
                
        self.jobdir = jobdir if jobdir is not None else self.name  # Job directory
        
        
    @property
    def name(self):
        return "pralines_{}_a{}_{}".format(self.larc, self.a0, self.wing.name)
        
        
    def setup(self, overwrite = None):
        """Generate a Pralines input file specific for this wing
        """
        # Create the job directory
        created = self.create_job_directory(overwrite)
        if not created: return False
        
        # Generate list of commands
        lines = []
        
        # Edit the wing type
        lines.append('WT')
        if type(self.wing) == wing.Elliptic:
            lines.append('E')
        elif type(self.wing) == wing.Rectangular or type(self.wing) == wing.Tapered:
            lines.append('T')
            
        # Edit the number of spanwise nodes
        lines.append('N')
        lines.append(self.wing.nSec + 1)  # Number of spanwise nodes per semispan
        
        # Edit the aspect ratio
        lines.append('RA')
        lines.append(self.wing.RA)
        
        # Edit the taper ratio
        if type(self.wing) == wing.Rectangular:
            lines.append('RT')
            lines.append(1.0)
        elif type(self.wing) == wing.Tapered:
            lines.append('RT')
            lines.append(self.wing.RT)
        
        # Edit the section lift slope
        lines.append('S')
        lines.append(self.a0)
        
        # Edit the low aspect ratio correction method
        lines.append('LC')
        if self.larc == 'Hodson': lines.append('H')
        elif self.larc == 'ModifiedSlender': lines.append('M')
        else: lines.append('C')  # Assume classical if no match found
        
        # Suppress output of C matrix and Fourier coefficients
        lines.append('C')
        
        # Set the output filename
        lines.append('F')
        lines.append('output.txt')
        
        # Advance to the operating conditions menu
        lines.append('A')
        
        # Set the root angle of attack
        lines.append('AA')
        lines.append('1.0')
        
        # Set the amount of washout to 0.0 deg
        lines.append('OW')  # Turns off optimum washout
        lines.append('W')
        lines.append(0.0)
        
        # Save the flight coefficients to the output file
        lines.append('S')
        
        # Output the lift distribution (saves to file 'liftcoefficient.dat')
        lines.append('WN')
        
        # Quit
        lines.append('Q')
        
        # Create the new input file in the job directory
        with open(self.jobdir + os.sep + 'input.txt', 'w') as inp_new:
            inp_new.write('\n'.join([str(line) for line in lines]))

        return True
        
        
    def execute(self):
        # Move into the job directory
        cwd = os.getcwd()
        os.chdir(self.jobdir)
        
        # Execute Pralines
        cmd = self.cmddir + os.sep + self.cmd
        print(cmd)
        os.system(cmd + " < input.txt")
        
        # Return to the original work directory
        os.chdir(cwd)
        
        
    def sec_cl(self):
        # Parse the output file
        with open(self.jobdir + os.sep + 'liftcoefficient.dat', 'r') as f:
            lines = f.readlines()
            
        ys = []
        cls = []
        for line in lines[1:]:
            y, cl = line.split(';')
            ys.append(float(y))
            cls.append(float(cl))
            
        return (ys, cls)

    
    @property
    def WingLiftSlope(self):
        # Parse the output file
        with open(self.jobdir + os.sep + 'output.txt', 'r') as f:
            lines = f.readlines()
        
        if type(self.wing) == wing.Elliptic:
            return float(lines[14].split()[2])
        else:
            return float(lines[16].split()[2])

    
    @property
    def WingLiftCoefficient(self):
        # Parse the output file
        with open(self.jobdir + os.sep + 'output.txt', 'r') as f:
            lines = f.readlines()
        
        if type(self.wing) == wing.Elliptic:
            return float(lines[36].split()[2])
        else:
            return float(lines[38].split()[2])
            
    
    def create_job_directory(self, overwrite = None):
        """Creates a directory for the Pralines analysis and copies necessary files
        """
        if os.path.isdir(self.jobdir):
            if overwrite is None:
                print("Directory already exists: " + self.jobdir)
                ow = input("Do you want to overwrite? (Y/n)\n")
                if len(ow) > 0 and (ow[0] == 'n' or ow[0] == 'N'):
                    overwrite = False
                else:
                    overwrite = True
                    
            if overwrite:
                shutil.rmtree(self.jobdir)
                time.sleep(0.01) # Give the file system some time...
            else:
                return False
    
        # Set up the job directory and copy MachUp
        os.mkdir(self.jobdir)
        
        return True
        
        
