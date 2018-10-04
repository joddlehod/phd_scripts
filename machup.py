import numpy as np
import os
import shutil
import time
import json
from collections import OrderedDict

import airfoil
import wing


def NewJoukowskiElliptic(af_thickness = 0.04, af_CLd = 0.0, af_npts = 40,
                         wing_RA = 'Circular', wing_b = 4.0 / np.pi, wing_npts = 80,
                         mu_template = 'input.json', mu_cmd = 'MachUp.exe', mu_dir = None,
                         mu_solver = 'nonlinear', mu_lowra_method = 'none'):
    a = airfoil.Joukowski(af_thickness, af_CLd, af_npts)
    w = wing.Elliptic(wing_RA, wing_b, wing_npts)
    m = MachUp(a, w, mu_template, mu_cmd, mu_dir, mu_solver, mu_lowra_method)
    return m


class MachUp(object):
    """Wrapper class for creating, running, and post-processing MachUp lifting-line analyses
    """
    def __init__(self, airfoil, wing, template = 'input.json', cmd = 'MachUp.exe', dir = None,
            solver = 'nonlinear', lowra_method = 'none'):
        """Constructor
        """
        self.template = template
        self.airfoil = airfoil
        self.wing = wing
        self.cmd = cmd
        self.dir = dir if dir is not None else self.name
        
        self._solver = solver
        self._lowra_method = lowra_method
        
        self._distributions = None
        self._forces = None
        
        
    def setup(self, overwrite = None):
        """Generate a MachUp input file specific for this wing
        """
        # Make sure the airfoil exists in the database
        error = self.airfoil.create_airfoil()
        if error: return None
        
        
        # Make sure the template file exists
        if not os.path.isfile(self.template):
            print("Error: Input template file '{}' does not exist.".format(self.template))
            return None

        # Create the job directory
        created = self.create_job_directory(overwrite)
        if not created: return False
        
        # Read and parse the template file
        with open(self.template, 'r') as inp_orig:
            input_data = json.load(inp_orig, object_pairs_hook = OrderedDict)
            
        # Set the solver type (linear | nonlinear)
        input_data['solver']['type'] = self._solver

        # Update the airfoil data
        input_data['wings']['wing_1']['airfoils'] = self.airfoil_data()
        
        # Update the wing data
        input_data['wings']['wing_1'] = self.wing_data(input_data['wings']['wing_1'])
        
        # Update the reference data
        input_data['reference'] = self.reference_data()

        # Create the new input file in the job directory
        with open(self.dir + os.sep + 'input.json', 'w') as inp_new:
            json.dump(input_data, inp_new, indent = 4)
            
        return True
        

    def execute(self):
        # Move into the job directory
        cwd = os.getcwd()
        os.chdir(self.dir)
        
        # Execute MachUp
        os.system(self.cmd + " input.json > stdout")
        
        # Return to the original work directory
        os.chdir(cwd)
        
        
    @property
    def distributions(self):
        """Read and parse the distributions result file
        """
        if self._distributions is None:
            self._distributions = np.genfromtxt(self.dir + os.sep + 'input_distributions.txt', names = True)
            
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
            with open(self.dir + os.sep + 'input_forces.json', 'r') as forces_file:
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
        if os.path.isdir(self.dir):
            if overwrite is None:
                print("Directory already exists: " + self.dir)
                ow = input("Do you want to overwrite? (Y/n)\n")
                if len(ow) > 0 and (ow[0] == 'n' or ow[0] == 'N'):
                    overwrite = False
                else:
                    overwrite = True
                    
            if overwrite:
                shutil.rmtree(self.dir)
                time.sleep(1.0) # Give the file system some time...
            else:
                return False
    
        # Set up the job directory and copy MachUp
        os.mkdir(self.dir)
        time.sleep(1.0) # Give the file system some time...
        shutil.copyfile(self.cmd, self.dir + os.sep + self.cmd)
        
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
        return self.dir + os.sep + 'input_view.panair'