import numpy as np


class Wing(object):
    """Defines the planform geometry of a finite wing

    This class stores the following parameters used to define the planform
    geometry of a finite wing. Currently only wings with uniform cross-section
    are supported.
    
        - Aspect ratio (RA)
        - Wingspan (b)
        - Section lift slope (CLa)
        - Number of spanwise sections (nSec) on a semispan
        
    The wing is divided into nSec spanwise sections per semispan. The sections
    are spaced using cosine clustering (coarse at the root, fine at the tip)
    with control points at the theta (not y) centerpoint of each section.
    """
    
    def __init__(self, RA, b, nSec, symm = True, suffix = None,
            root_clustering = False, tip_clustering = True):
        """Constructor
        
        Wing object constructor
        
        Inputs
        ------
        RA: Aspect ratio ('Circular' = 4.0 / pi)
        b: Wingspan
        nSec: Number of spanwise wing sections per semispan
        symm: Use symmetry plane? True/False
        suffix: String to append to the end of the wing name
        root_clustering: Use cosine-clustering at the root of the wing?
        tip_clustering: Use cosine-clustering at the tip of the wing?
        """
        # Aspect Ratio
        self.RAString = RA
        if RA == 'Circular': self.RA = 4.0 / np.pi
        else: self.RA = RA

        self.b = b                  # Wingspan
        self.nSec = nSec            # Number of spanwise sections per semispan
        
        # Initialize sections / spanwise coordinates
        self.symm = symm
        self.root_clustering = root_clustering
        self.tip_clustering = tip_clustering
        self.create_sections()
    
        self.basename = 'ra{}_grid{}'.format(self.RAString, self.nSec)
        if self.root_clustering: self.basename += '_rcOn'
        if not self.tip_clustering: self.basename += '_tcOff'
        if not self.symm: self.basename += '_full'
        if suffix is not None: self.basename += '_{}'.format(suffix)

    
    def create_sections(self):
        """Create the spanwise section definitions for the wing
        
        This function is used to initialize the spanwise coordinates of each
        section endpoint and centerpoint. The sections are distributed along
        the wingspan with the centerpoints at the theta (not y) centerpoint
        of each section. The section distribution matches that of the MachUp
        source code.
        
        If the wing is symmetric (self.symm == True), only the positive-y
        semispan is modeled. Otherwise, both semispans are modeled and the
        total number of spanwise sections is 2*nSec.
        """
        linear = False
        if self.root_clustering and self.tip_clustering:
            theta_start = 0.0
            theta_end = np.pi
            off = 1.0
            fac = 0.5
            
        elif self.root_clustering:
            theta_start = 0.0
            theta_end = np.pi / 2.0
            off = 1.0
            fac = 1.0
            
        elif self.tip_clustering:
            theta_start = np.pi / 2.0
            theta_end = np.pi
            off = 0.0
            fac = 1.0
            
        else:
            linear = True
            
        if linear:
            self.y = np.linspace(0.0, 0.5, self.nSec + 1)
            self.yc = np.asarray([(y1 + y2) / 2 for y1, y2 in zip(self.y[:-1], self.y[1:])])
            
        else:
            theta = np.linspace(theta_start, theta_end, self.nSec + 1, True)
            thetac = np.asarray([(t1 + t2) / 2 for t1, t2 in zip(theta[:-1], theta[1:])])
        
            self.y = self.b / 2 * fac * (off - np.cos(theta))
            self.yc = self.b / 2 * fac * (off - np.cos(thetac))
        
        if not self.symm:
            self.y = np.concatenate([self.y[::-1], self.y[1::]])
            self.yc = np.concatenate([self.yc[::-1], self.y[::]])
            
        self.theta = self.thetacoord(self.y)
        self.thetac = self.thetacoord(self.yc)

        self.c = self.chord_theta(self.theta)
        self.cc = self.chord_theta(self.thetac)
        
        
    @property
    def Area(self):
        """Calculate the planform area of the wing
        """
        return self.b**2 / self.RA
        
        
    @property
    def c_avg(self):
        """Calculate the average chord length of the wing
        """
        return self.Area / self.b
        
        
    def thetacoord(self, y):
        """Calculate theta-coordinate (cosine clustering) at this y-coordinate
        """
        return np.arcsin(np.sqrt(1.0 - (2.0 * y / self.b)**2))


    def ycoord(self, theta):
        """Calculate y-coordinate at this theta-coordinate (cosine clustering)
        """
        return (0.5 * self.b * np.sqrt(1.0 - np.sin(theta)**2)
                * np.sign(theta - np.pi / 2.0))
        
        
    @property
    def c_root(self):
        """Get the root chord length
        """
        if self.symm: return self.c[0]
        else: return self.c[self.nSec]
        
        
    @property
    def c_tip(self):
        """Get the tip chord length
        """
        return self.c[-1]
        
        
    @property
    def sec_Area(self):
        """Calculate the area of each section along the wingspan
        """
        return (self.c_integral(self.y[1:]) - self.c_integral(self.y[:-1]))

        
class Rectangular(Wing):
    """Defines the planform geometry of a rectangular wing
    
    This class provides data and methods associated with a rectangular wing.
    The number of sections is defined by the user, and the wing is divided
    using cosine-clustering toward the wing tip.
    """
    def __init__(self, RA, b, nSec, symm = True, suffix = None,
            root_clustering = False, tip_clustering = True):
        """Constructor
        
        Elliptic wing object constructor
        
        Inputs
        ------
        RA:         Aspect ratio
        b:          Wingspan
        nSec:       Number of spanwise sections per semispan
        symm:       Use symmetry plane? True/False
        suffix:     String to append to the end of the wing name
        """
        super().__init__(RA, b, nSec, symm, suffix, root_clustering, tip_clustering)

                
    def chord_theta(self, theta):
        """Calculate the chord length at this theta-coordinate.
        
        The specified theta-coordinate should range between 0 and pi, where:
            theta == 0    corresponds to the left wing tip (y = -b/2)
            theta == pi/2 corresponds to the wing root (y = 0)
            theta == pi   corresponds to the right wing tip (y = b/2)
        """
        if hasattr(theta, '__iter__'):
            return np.ones(len(theta)) * self.c_avg
        else:
            return self.c_avg
        
        
    def c_integral(self, y):
        """Calculate the indefinite integral of the chord at this y-coordinate
        """
        return (self.c_avg * y)


    @property
    def name(self):
        return 'rectangular_{}'.format(self.basename)    


class Tapered(Wing):
    """Defines the planform geometry of a tapered wing
    
    This class provides data and methods associated with a rectangular wing.
    The number of sections is defined by the user, and the wing is divided
    using cosine-clustering toward the wing tip.
    """
    def __init__(self, RA, RT, b, nSec, symm = True, suffix = None,
            root_clustering = False, tip_clustering = True):
        """Constructor
        
        Elliptic wing object constructor
        
        Inputs
        ------
        RA:         Aspect ratio
        RT:         Taper ratio
        b:          Wingspan
        nSec:       Number of spanwise sections per semispan
        symm:       Use symmetry plane? True/False
        suffix:     String to append to the end of the wing name
        """
        self.RT = RT
        super().__init__(RA, b, nSec, symm, suffix, root_clustering, tip_clustering)

                
    def chord_theta(self, theta):
        """Calculate the chord length at this theta-coordinate.
        
        The specified theta-coordinate should range between 0 and pi, where:
            theta == 0    corresponds to the left wing tip (y = -b/2)
            theta == pi/2 corresponds to the wing root (y = 0)
            theta == pi   corresponds to the right wing tip (y = b/2)
        """
        return (2.0 * self.b / (self.RA * (1.0 + self.RT)) *
                (1.0 - (1.0 - self.RT)*np.abs(np.cos(theta))))
        
        
    def c_integral(self, y):
        """Calculate the indefinite integral of the chord at this y-coordinate
        """
        return (2.0 * self.b  / (self.RA * (1.0 + self.RT)) *
                (y - (1.0 - self.RT) * 2.0 * y**2 / self.b))


    @property
    def name(self):
        return 'tapered_rt{}_{}'.format(self.RT, self.basename)    


class Elliptic(Wing):
    """Defines the planform geometry of an elliptic wing
    
    This class provides data and methods associated with an elliptic wing.
    The number of sections is defined by the user, and the wing is divided
    using cosine-clustering toward the wing tip.
    """
    
    def __init__(self, RA, b, nSec, symm = True, suffix = None,
            root_clustering = False, tip_clustering = True):
        """Constructor
        
        Elliptic wing object constructor
        
        Inputs
        ------
        RA:         Aspect ratio
        b:          Wingspan
        nSec:       Number of spanwise sections per semispan
        symm:       Use symmetry plane? True/False
        suffix:     String to append to the end of the wing name
        """
        super().__init__(RA, b, nSec, symm, suffix, root_clustering, tip_clustering)
        
    
    def chord_theta(self, theta):
        """Calculate the chord length at this theta-coordinate.
        
        The specified theta-coordinate should range between 0 and pi, where:
            theta == 0    corresponds to the left wing tip (y = -b/2)
            theta == pi/2 corresponds to the wing root (y = 0)
            theta == pi   corresponds to the right wing tip (y = b/2)
        """
        return (4.0 * self.b) / (np.pi * self.RA) * np.sin(theta)
        
        
    def chord_y(self, y):
        """Calculate the chord length at this y-coordinate.
        
        The specified y-coordinate should range between -b/2 and b/2, where:
            y == -b/2 corresponds to the left wing tip
            y ==    0 corresponds to the root
            y ==  b/2 corresponds to the right wing tip
        """
        return ((4.0 * self.b) / (np.pi * self.RA) *
                np.sqrt(1.0 - (2.0 * y / self.b)**2))

                
    def c_integral(self, y):
        """Calculate the indefinite integral of the chord at this y-coordinate
        """
        return ((4.0 * self.b) / (np.pi * self.RA) *
                (0.5 * y * np.sqrt(1.0 - (2.0 * y / self.b)**2) +
                self.b / 4.0 * np.arcsin(2.0 * y / self.b)))


    @property
    def name(self):
        return 'elliptic_{}'.format(self.basename)