import numpy as np

def extrapolate(m1, m2, m3, f1, f2, f3, p = 2, reltol = 1.0e-12):
    if m3 == m2 * 2 and m2 == m1 * 2:
        return re_124(m1, m2, m3, f1, f2, f3)
    else:
        return re_arbitrary(m1, m2, m3, f1, f2, f3, p, reltol)
    
    
def re_124(m1, m2, m3, f1, f2, f3):
    f21 = f2 + (f2 - f1) / 3.
    f32 = f3 + (f3 - f2) / 3.
    re = f32 + (f32 - f21) / 15.
    return (re, 2)


def re_arbitrary(m1, m2, m3, f1, f2, f3, p = 2, reltol = 1.0e-12):
    error = 1.0
    r21 = np.power(m1 / m2, 1. / 3.)
    r32 = np.power(m2 / m3, 1. / 3.)

    print("{:>4}, {:>18}, {:>18}, {:>18}, {:>18}, {:>18}, {:>18}".format(
            "iter", "extr. value 1", "extr. value 2", "avg. extr. value",
            "order 1", "order 2", "avg. order"))
    for i in range(100):
        fext1 = extrap(f1, f2, r21, p)
        fext2 = extrap(f2, f3, r32, p)
        fextavg = average(fext1, fext2)
        p1 = order(f1, f2, fextavg, r21)
        p2 = order(f2, f3, fextavg, r32)
        if hasattr(p1, '__iter__'):
            pavg = np.asarray([min(a1, a2) for a1, a2 in zip(p1, p2)])
        else:
            pavg = min(p1, p2)

        if i == 0:
            error1 = abs(pavg - p)

        error = abs(pavg - p) / error1
        p = pavg

#        print("{:>4}, {:>18}, {:>18}, {:>18}, {:>18}, {:>18}, {:>18}".format(
#                i, fext1, fext2, fextavg, p1, p2, pavg))
        if np.max(error) < reltol: break
        
    return (fextavg, pavg)


def re2(m1, m2, m3, f1, f2, f3, p = 2, reltol = 1.0e-12):
    r21 = np.power(m1 / m2, 1. / 3.)
    r32 = np.power(m2 / m3, 1. / 3.)
    error = 1
    print("{:>4}, {:>18}, {:>18}".format("iter", "extr. value", "order"))
    for i in range(100):
        s = np.sign( (f3 - f2) / (f2 - f1) )
        q_p = np.log( (r21**p - s) / (r32**p - s) )
        p1 = abs(np.log(abs( (f3 - f2) / (f2 - f1) )) + q_p) / np.log(r21)
        error = abs(p1 - p)
        p = p1
        print("{:>4}, {:>18.12E}, {:>18.12E}".format(i, extrap(f1, f2, r21, p), p))
        if error < reltol: break


def extrap(f1, f2, r, p):
    return f1 + (f1 - f2) / (r**p - 1.0)


def order(f1, f2, favg, h):
    return np.log(abs(favg - f2) / abs(favg - f1)) / np.log(h)


def average(v1, v2):
    return (v1 + v2) / 2.0
