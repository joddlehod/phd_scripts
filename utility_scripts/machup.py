import numpy as np
import os
import shutil
import time
import json
from collections import OrderedDict

import phd_scripts
from phd_scripts.utility_scripts import airfoil
from phd_scripts.utility_scripts import wing


class MachUp(object):
    """Wrapper class for creating, running, and post-processing MachUp lifting-line analyses
    """
    def __init__(self, airfoil, wing, solver = 'nonlinear', lowra_method = 'none',
            template = 'input.json', templatedir = None, cmd = 'MachUp.exe',
            cmddir = None, jobdir = None):
        """Constructor
        """
        # Set the wing geometry
        self.airfoil = airfoil
        self.wing = wing
        
        # Set the solver parameters
        self._solver = solver
        self._lowra_method = lowra_method

        # Set the file and path names
        self.template = template
        self.templatedir = templatedir if templatedir is not None else (
                phd_scripts.__path__[0] + os.sep + 'templates')

        self.cmd = cmd
        self.cmddir = cmddir if cmddir is not None else (
                phd_scripts.__path__[0] + os.sep + 'executables')

        self.jobdir = jobdir if jobdir is not None else self.name
        
        # Result variables
        self._distributions = None
        self._forces = None
        
        
    def setup(self, overwrite = None):
        """Generate a MachUp input file specific for this wing
        """
        # Make sure the airfoil exists in the database
        error = self.airfoil.create_airfoil()
        if error: return None
        
        # Make sure the template file exists
        template = self.templatedir + os.sep + self.template
        if not os.path.isfile(template):
            print("Error: Input template file '{}' does not exist.".format(template))
            return None

        # Create the job directory
        created = self.create_job_directory(overwrite)
        if not created: return False
        
        # Read and parse the template file
        with open(template, 'r') as inp_orig:
            input_data = json.load(inp_orig, object_pairs_hook = OrderedDict)
            
        # Set the airfoild database location
        input_data['airfoil_DB'] = self.airfoil.dbdir
            
        # Set the solver type (linear | nonlinear)
        input_data['solver']['type'] = self._solver

        # Update the airfoil data
        input_data['wings']['wing_1']['airfoils'] = self.airfoil_data()
        
        # Update the wing data
        input_data['wings']['wing_1'] = self.wing_data(input_data['wings']['wing_1'])
        
        # Update the reference data
        input_data['reference'] = self.reference_data()

        # Create the new input file in the job directory
        with open(self.jobdir + os.sep + 'input.json', 'w') as inp_new:
            json.dump(input_data, inp_new, indent = 4)
            
        return True
        

    def execute(self):
        # Move into the job directory
        cwd = os.getcwd()
        os.chdir(self.jobdir)
        
        # Execute MachUp
        os.system(self.cmddir + os.sep + self.cmd + " input.json > stdout")
        
        # Return to the original work directory
        os.chdir(cwd)
        
        
    @property
    def distributions(self):
        """Read and parse the distributions result file
        """
        if self._distributions is None:
            output_file = self.jobdir + os.sep + 'input_distributions.txt'
            self._distributions = np.genfromtxt(output_file, names = True)
            
        return self._distributions
        
        
    @property
    def sec_x(self):
        """Get the section x-coordinates from the distribution file
        """
        return self.distributions['ControlPointx']
        
        
    @property
    def sec_y(self):
        """Get the section y-coordinates from the distribution file
        """
        return self.distributions['ControlPointy']
        
        
    @property
    def sec_z(self):
        """Get the section z-coordinates from the distribution file
        """
        return self.distributions['ControlPointz']
        
        
    @property
    def sec_c(self):
        """Get the section chord distribution from the distribution file
        """
        return self.distributions['Chord']
        
        
    @property
    def sec_twist(self):
        """Get the section twist distribution from the distribution file
        """
        return self.distributions['Twistdeg']
        
        
    @property
    def sec_Area(self):
        """Get the section area distribution from the distribution file
        """
        return self.distributions['Area']
        
        
    @property
    def sec_AoA(self):
        """Get the section effective angle of attack from the distribution file
        """
        return self.distributions['Section_Alphadeg']
        
        
    @property
    def sec_CL(self):
        """Get the section lift distribution from the distribution file
        """
        return self.distributions['Section_CL']
        
        
    @property
    def sec_CDp(self):
        """Get the section parasitic drag distribution from the distribution file
        """
        return self.distributions['Section_CD_parasitic']
        
        
    @property
    def sec_alphaL0(self):
        """Get the section zero-lift angle of attack from the distribution file
        """
        return self.distributions['Section_alpha_L0deg']
        
        
    @property
    def forces(self):
        """Read and parse the forces result file
        """
        if self._forces is None:
            with open(self.jobdir + os.sep + 'input_forces.json', 'r') as forces_file:
                self._forces = json.load(forces_file, object_pairs_hook = OrderedDict)
                
        return self._forces
            
            
    @property
    def CL(self):
        """Get the wing lift coefficient predicted by this MachUp analysis
        """
        return self.forces['total']['myairplane']['CL']
        
        
    @property
    def CD(self):
        """Get the wing drag coefficient predicted by this MachUp analysis
        """
        return self.forces['total']['myairplane']['CD']

        
    def create_job_directory(self, overwrite = None):
        """Creates a directory for the MachUp analysis and copies necessary files
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
                time.sleep(1.0) # Give the file system some time...
            else:
                return False
    
        # Set up the job directory
        os.mkdir(self.jobdir)
        
        return True
        
        
    def airfoil_data(self):
        """Create a dictionary for the airfoil data
        """
        # Set the airfoil name
        af_data = {}
        af_data[self.airfoil.name] = ""
        
        return af_data
        
        
    def wing_data(self, wing_template_data):
        """Create a dictionary for the wing data
        """
        # Set the planform info
        wing_template_data['span'] = self.wing.b / 2.0
        wing_template_data['root_chord'] = self.wing.c_root
        wing_template_data['tip_chord'] = self.wing.c_tip
        if type(self.wing) == wing.Elliptic: 
            wing_template_data['tip_chord'] = -1.0
        
        # Set the grid size
        wing_template_data['grid'] = int(self.wing.nSec)  # Cast to int because it might be a numpy object
                                                          # which gives "TypeError: # is not JSON serializable"

        # Set the low-aspect-ratio method
        wing_template_data['low_aspect_ratio_method'] = self._lowra_method
        
        return wing_template_data
        
     
    def reference_data(self):
        ref_data = {}
        ref_data['area'] = self.wing.Area
        ref_data['longitudinal_length'] = self.wing.b
        ref_data['lateral_length'] = self.wing.c_avg
        return ref_data
        
        
    @property
    def name(self):
        return "machup_{}_{}".format(self.airfoil.name, self.wing.name)
        
        
    @property
    def panair_input_file(self):
        return self.jobdir + os.sep + 'input_view.panair'