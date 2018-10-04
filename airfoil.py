import numpy as np
import os
import shutil
import json
from collections import OrderedDict


class FlatPlate(object):
    """Defines the 2D airfoil characteristics of a flat plate
    """
    def __init__(self):
        """Constructor
        """
        self.CL_alpha = 2 * np.pi
        self.name = "flat_plate"
    
    
    def create_airfoil(self, cmd = None, dbdir = "AirfoilDatabase"):
        pass


class Joukowski(object):
    """Defines the characteristics of a 2D Joukowski airfoil
    
    This class is used to define a 2D Joukowski airfoil
    """
    
    def __init__(self, t, cld, npts):
        """Constructor
        
        Inputs
        ------
        t = Maximum thickness
        cld = Design lift coefficient
        npts = Number of points around the airfoil perimeter
        """
        self.t = t
        self.cld = cld
        self.npts = npts
        if npts % 2 == 1:
            print("Error: Airfoil points must be even!")
            print("       Setting number of points to {}".format(npts + 1))
            self.npts += 1
    
    
    @property
    def name(self):
        name = "joukowski_t{}_cl{}_af{}".format(self.t, self.cld, self.npts)
        return name.replace('.', 'p')


    def create_airfoil(self, cmd = "Joukowski.exe", dbdir = "AirfoilDatabase"):
        # Only run the panel code if the airfoil doesn't already exist in the database
        airfoil_json_name = dbdir + os.sep + self.name + ".json"
        airfoil_profile_name = dbdir + os.sep + self.name + "_profile.txt"
        if ((not os.path.isfile(airfoil_json_name)) or
                (not os.path.isfile(airfoil_profile_name))):
            if os.path.isfile(airfoil_json_name): os.remove(airfoil_json_name)
            if os.path.isfile(airfoil_profile_name): os.remove(airfoil_profile_name)

            # Make sure the executable exists in the current directory
            if not os.path.isfile(cmd):
                print("Error: Missing panel code executable {}".format(cmd))
                return True
        
            # Write the panel code input commands to a file
            with open("joukowski_input.txt", "w") as input_file:
                input_file.write("1\n")  # Select Joukowski airfoil
                input_file.write("{}\n".format(self.t))  # Airfoil thickness
                input_file.write("{}\n".format(self.cld))  # Design lift coefficient
                input_file.write("0.0\n")  # Angle of attack (doesn't change relevant results)
                input_file.write("0.25\n")  # x/c location for moment calculation (doesn't change relevant results)
                input_file.write("0.0\n")  # y/c location for moment calculation (doesn't change relevant results)
                input_file.write("n\n")  # Don't plot pressure distributions
                input_file.write("n\n")  # Don't plot streamlines
                input_file.write("y\n")  # Write the airfoil profile
                input_file.write("{}\n".format(self.npts))  # Number of points on profile
            
            # Execute the panel code
            os.system("{} < joukowski_input.txt > joukowski_stdout".format(cmd))
            
            # Read the output and extract CL,alpha and alpha_L0
            with open('joukowski_stdout', 'r') as stdout:
                stdout_lines = stdout.readlines()
            self.CL_alpha = float(stdout_lines[15].split()[4])
            self.alpha_L0 = np.radians(float(stdout_lines[14].split()[3]))

            # Move the output file to the correct filename
            output_file = "{}.txt".format(self.npts)
            if not os.path.isfile(output_file):
                print("Error: Panel code output file is missing! ({})".format(output_file))
                return True
                
            os.rename(output_file, airfoil_profile_name)

            # Make sure the JSON template file exists
            json_template_name = "flat_plate"
            json_template_file = json_template_name + ".json"
            if not os.path.isfile(json_template_file):
                json_template_file = dbdir + os.sep + json_template_file
                if not os.path.isfile(json_template_file):
                    print("Error: Missing JSON template file {}".format(json_template_file))
                    return True
                
            # Read the JSON file template
            with open(json_template_file, "r") as json_template:
                json_data_template = json.load(json_template, object_pairs_hook = OrderedDict)
                
            # Edit the airfoil name
            json_data_new = OrderedDict()
            json_data_new[self.name] = json_data_template[json_template_name]
            json_data_new[self.name]['properties']['CL_alpha'] = self.CL_alpha
            json_data_new[self.name]['properties']['alpha_L0'] = self.alpha_L0
            
            # Write the new JSON file
            with open(airfoil_json_name, 'w') as json_new:
                json.dump(json_data_new, json_new, indent = 4)
                
            # Clean up temporary files
            os.remove('joukowski_input.txt')
            os.remove('joukowski_stdout')

        else:
            # Airfoil files already exist, parse existing JSON file
            with open(airfoil_json_name) as affile:
                afdata = json.load(affile, object_pairs_hook = OrderedDict)
                
            self.CL_alpha = afdata[self.name]["properties"]["CL_alpha"]
            self.alpha_L0 = afdata[self.name]["properties"]["alpha_L0"]
            
        return False
