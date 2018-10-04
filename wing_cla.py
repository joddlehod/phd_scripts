import numpy as np
from scipy.special import ellipe


def resistance_parallel(r1, r2):
    """Calculate the effective resistance of two parallel resistors
    
    Inputs:
        r1 = Value of resistor 1
        r2 = Value of resistor 2
    """
    return ((r1)**(-1) + (r2)**(-1))**(-1)


def a_classical(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using classical lifting-line theory
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left( \frac{1}{a_0} + \frac{1}{\pi A} \right) ^{-1}
            
    which corresponds to the approximation given by Prandtl in his original
    development of classical lifting line theory in 1918.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate the individual resistance values
    r1 = a0
    r2 = np.pi * A

    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)
    
    
def a_slender(A):
    """Calculate the wing lift slope using slender wing theory
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \frac{\pi A}{2}
            
    which corresponds to the approximation given by Jones in his original
    development of slender wing theory in 1946. Note that this equation is
    independent of section lift slope (a0).
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
    """
    # Calculate the individual resistance values
    r1 = np.inf
    r2 = np.pi * A / 2.0

    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)
    
    
def a_helmbold(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using Helmbold's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left[ \sqrt {\frac{1}{{a_0}^2} + \frac{1}{(\pi A)^2}}
                + \frac{1}{\pi A} \right] ^{-1}            
                
    which corresponds to the approximation given by Helmbold in 1942.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate the individual resistance values
    r1 = np.sqrt(a0**(-2) + (np.pi * A)**(-2))**(-1)
    r2 = np.pi * A

    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)
    
    
def a_jones(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using Helmbold's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left( \frac{E}{a_0} + \frac{1}{\pi A} \right)

    which corresponds to the approximation given by Jones in 1941.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate the eccentricity of the ellipse
    k = 1 / (np.pi * A / 4.0)
    
    # Calculate the parameter
    h2 = 1.0 - k**2
    
    # Use the complete integral of the second kind to calculate the perimeter
    # of an ellipse
    E = ellipe(h2)
    
    # Calculate the individual resistance values
    r1 = a0 / E
    r2 = np.pi * A
    
    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)


def a_vandyke(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using van Dyke's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left\{ \frac{1}{a_0} + \frac{1 + \frac{4 a_0}{\pi^3 A} \left[
                \ln(\pi A) - \frac{9}{8} \right ]}{\pi A  } \right\}^{-1}

    which corresponds to the approximation given by van Dyke in 1964.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate the individual resistance values
    r1 = a0
    r2 = (np.pi * A) / (1 + 4.0 * a0 / (np.pi**3 * A) *
            (np.log(np.pi * A) - 9.0 / 8.0))
    
    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)
    
    
def a_germain(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using van Dyke's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left( \frac{1}{a_0} + \frac{1 + \frac{4 a_0}{\pi^3 A}
                    \ln(1 + \pi e^{-9/8} A)}{\pi A} \right)

    which corresponds to the approximation given by Germain in 1967 and
    corrected by van Dyke in 1975.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate the individual resistance values
    r1 = a0
    r2 = (np.pi * A) / (1.0 + (4 * a0) / (np.pi**3 * A) *
            np.log(1.0 + np.pi * np.exp(-9.0 / 8.0) * A))
    
    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)

    
def a_hauptmanmiloh(A):
    """Calculate the wing lift slope using Hauptman and Miloh's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left\{\begin{matrix} \left[ \frac{E^2(h)}{\pi A + (4k^3/h)
                \ln(1/k + h/k)} + \frac{1}{\pi A} \right]^{-1}, &
                k=\frac{\pi A}{4} \le 1 \\ \left[ \frac{E^2(h)}{4 (k +
                \sin^{-1}(h)/h)} + \frac{1}{\pi A} \right]^{-1}, &
                k=\frac{4}{\pi A} \le 1 \end{matrix}\right.

    which corresponds to the approximation given by Hauptman and Miloh in 1986.
    
    Note that a0 does not appear in the equations because they were derived
    explicitly for a flate plate with a0 = 2*pi.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
    """
    if A < (4.0 / np.pi):
        # Slender wing
        # Calculate the eccentricity and parameter for the ellipse
        k = (np.pi * A) / 4.0
        h = np.sqrt(1.0 - k**2)
        
        # Calculate the perimeter of the ellipse using the complete elliptic
        # integral of the second kind
        E = ellipe(h**2)
        
        # Calculate the resistance value r1
        r1 = (np.pi * A + (4.0 * k**3 / h * np.log((1.0 + h) / k))) / E**2
    
    elif A > (4.0 / np.pi):
        # High-aspect-ratio wing
        # Calculate the eccentricity and parameter for the ellipse
        k = 4.0 / (np.pi * A)
        h = np.sqrt(1.0 - k**2)
        
        # Calculate the perimeter of the ellipse using the complete elliptic
        # integral of the second kind
        E = ellipe(h**2)
        
        # Calculate the resistance value r1
        r1 = 4 * (k + np.arcsin(h) / h) / E**2
        
    else:
        # Circular wing
        r1 = 32.0 / (2.0 + np.pi**2)
    
    # Calculate the resistance value r2
    r2 = np.pi * A
    
    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)
    
    
def a_kuchemann(A, a0 = 2.0 * np.pi):
    """Calculate the wing lift slope using Kuchemann's approximation
    
    This function calculates the wing lift slope of a finite elliptic wing
    using the equation
    
            a = \left[ \frac{1-\pi n \cot(\pi n)}{2 n a_0} + \frac{2n}{\pi A}
                \right]^{-1}
                
        where
        
            n = 1 - \frac{1}{2} \left[ 1 + \left( \frac{a_0}{\pi A} \right)^2
                \right]^{-1/4}
    
    which corresponds to the approximation given by Kuchemann in 1952.
    
    Inputs:
        A = Aspect ratio of wing (b^2 / Sw)
        a0 = 2D section wing lift slope (2*pi for thin airfoils)
    """
    # Calculate Kuchemann's n parameter
    n = 1.0 - 0.5 * (1.0 + (a0 / (np.pi * A))**2)**(-0.25)
    
    # Calculate the individual resistance values
    r1 = (2.0 * n * a0) / (1.0 - np.pi * n / np.tan(np.pi * n))
    r2 = (np.pi * A) / (2.0 * n)
    
    # Calculate the wing lift slope using the parallel resistors method
    return resistance_parallel(r1, r2)


def a_modified_slender(A, a0 = 2.0 * np.pi):
    r1 = a0
    r2 = np.pi * A / 2.0
    return resistance_parallel(r1, r2)
    
    
def a_hodson(A, a0 = 2.0 * np.pi):
    r1 = a0
    r2 = A * (np.pi - np.arctan(2.0 * a0 / (np.pi * A)))
    return resistance_parallel(r1, r2)


def a_krienes():
    A =  [0.637, 2.550, 6.370]
    cla = [0.990, 2.990, 4.550]
    h2 = A_to_h2(A)

    return (A, h2, cla)


def a_kinner():
    A =  [1.272]
    cla = [1.820]
    h2 = A_to_h2(A)

    return (A, h2, cla)


def a_jordan():
    A =  [4 / np.pi]
    cla = [1.7900230]
    h2 = A_to_h2(A)

    return (A, h2, cla)


def a_medan():
    A =  [x / np.pi for x in [1, 2, 4, 8, 16]]
    cla = [0.496, 0.969, 1.79004, 2.944, 4.151]
    h2 = A_to_h2(A)

    return (A, h2, cla)


def A_to_h2(Arange):
    h2range = []
    for A in Arange:
        if A < 4 / np.pi:
            h2range.append(-(1 - ((np.pi * A) / 4)**2))
        else:
            h2range.append( (1 - (4 / (np.pi * A))**2))

    return np.asarray(h2range)


    
    