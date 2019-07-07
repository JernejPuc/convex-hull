"""Variations on Andrew's monotone chain convex hull algorithm v19.05.12 by Jernej Puc."""


#####################################################################################################
# MODULES

import sys                                  # CLI
from random import uniform, triangular      # Random point distributions
from time import perf_counter               # Performance evaluation
import matplotlib.pyplot as plt             # Visualisation


#####################################################################################################
# VARIATIONS

def public_version(P, filtered=False):
    """Constructs the upper and lower hull sections separately (each point is considered twice)."""

    # Preprocess
    if filtered:
        minx = min(P)
        maxx = max(P)
        miny = min(P, key=lambda p: p[1])
        maxy = max(P, key=lambda p: p[1])

        P = sorted(p for p in P if not_inside(p, minx, maxx, miny, maxy))
    else:
        P.sort()
    
    # Build upper hull section
    upper = []

    for p in P:
        while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], p):
            upper.pop()

        upper.append(p)
    
    # Build lower hull section
    lower = []

    for p in reversed(P):
        while len(lower) > 1 and is_left_turn(lower[-2], lower[-1], p):
            lower.pop()

        lower.append(p)
    
    # Merge hull sections
    return upper[:-1] + lower


def andrews_version(P, filtered=False):
    """Determines, to which section the point can go. Each point is thus cosidered only once."""
    
    # Preprocess
    if filtered:
        minx = min(P)
        maxx = max(P)
        miny = min(P, key=lambda p: p[1])
        maxy = max(P, key=lambda p: p[1])

        P = sorted(p for p in P if not_inside(p, minx, maxx, miny, maxy))
    else:
        P.sort()
    
    # Data structures
    upper = []
    lower = []

    # Endpoints
    p0 = P[0]
    pn = P[-1]

    # Bounds
    miny = min(p0[1], pn[1])
    maxy = max(p0[1], pn[1])

    # Line of separation
    k = (pn[1] - p0[1])/(pn[0] - p0[0] + 1e-12)
    n = p0[1] - k*p0[0]

    # Add left endpoint
    upper.append(p0)
    lower.append(p0)

    # Construct the middle of the upper and lower hull sections
    for j in range(1, len(P)-1):
        p = P[j]

        if p[1] > maxy:
            while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], p):
                upper.pop()

            upper.append(p)

        elif p[1] < miny:
            while len(lower) > 1 and not is_left_turn(lower[-2], lower[-1], p):
                lower.pop()
            
            lower.append(p)

        else:
            if p[1] > k*p[0] + n:
                while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], p):
                    upper.pop()

                upper.append(p)

            else:
                while len(lower) > 1 and not is_left_turn(lower[-2], lower[-1], p):
                    lower.pop()
                
                lower.append(p)

    # Add right endpoint (only once due to merging that follows)
    while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], pn):
        upper.pop()

    while len(lower) > 1 and not is_left_turn(lower[-2], lower[-1], pn):
        lower.pop()

    upper.append(pn)

    # Reverse lower hull section
    lower.reverse()

    # Merge hull sections
    return upper + lower


def optimised_version(P, filtered=None):
    """Considers only relevant points and determines, where the (relevant) point can go."""

    # Preprocess
    P.sort()

    # Data structures
    upper = []
    lower = []

    # Endpoints
    p0 = P[0]
    pn = P[-1]

    # Initial line(s) of separation
    ku = (pn[1] - p0[1])/(pn[0] - p0[0] + 1e-12)
    nu = p0[1] - ku*p0[0]
    kl = ku
    nl = nu

    # Add left endpoint
    upper.append(p0)
    lower.append(p0)

    # Construct the middle of the upper and lower hull sections
    for j in range(1, len(P)-1):
        p = P[j]

        if p[1] > ku*p[0] + nu:
            while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], p):
                upper.pop()

            upper.append(p)

            # Update upper line of separation
            ku = (pn[1] - p[1])/(pn[0] - p[0] + 1e-12)
            nu = p[1] - ku*p[0]

        elif p[1] < kl*p[0] + nl:
            while len(lower) > 1 and not is_left_turn(lower[-2], lower[-1], p):
                lower.pop()
            
            lower.append(p)

            # Update lower line of separation
            kl = (pn[1] - p[1])/(pn[0] - p[0] + 1e-12)
            nl = p[1] - kl*p[0]

    # Add right endpoint (only once due to merging that follows)
    while len(upper) > 1 and is_left_turn(upper[-2], upper[-1], pn):
        upper.pop()

    while len(lower) > 1 and not is_left_turn(lower[-2], lower[-1], pn):
        lower.pop()

    upper.append(pn)

    # Reverse lower hull section
    lower.reverse()

    # Merge hull sections
    return upper + lower


#####################################################################################################
# AUXILIARY

def point_cloud(n, w=1000., h=1000., distribution=uniform):
    """Returns a list of random points with coordinates (x,y) in general position."""

    return [(distribution(-w,w), distribution(-h,h)) for _ in range(n)]


def is_left_turn(p, q, r):
    """Returns True if the turn of pq -> qr is counter-clockwise and False otherwise."""

    return (q[0] - p[0])*(r[1] - p[1]) > (r[0] - p[0])*(q[1] - p[1])


def not_inside(p, a, c, b, d):
    """Returns True if p does not lie inside quadrilateral abcd and False otherwise."""
    if p == a or p == b or p == c or p == d:
        return True
    
    return not(is_left_turn(a,b,p) and is_left_turn(b,c,p) and is_left_turn(c,d,p) and is_left_turn(d,a,p))


def time_alg(alg, P, filtered=False):
    """Runs and times the running time of an algorithm on the given point cloud."""

    ctr = perf_counter()
    alg(P, filtered)

    return perf_counter() - ctr


def plot_hull(hull, P=[]):
    """Plots the convex hull and points within, if given."""

    fig,ax = plt.subplots()

    for i in range(len(hull)-1):
        ax.plot((hull[i][0], hull[i+1][0]), (hull[i][1], hull[i+1][1]), 'r-')
    
    ax.plot([p[0] for p in P], [p[1] for p in P], 'ko')

    plt.show()


#####################################################################################################
# TESTING (CLI)

if __name__ == '__main__':
    
    if len(sys.argv) < 4:
        raise IndexError('Missing input arguments.')

    # Filter flag
    filtered = ('-f' in sys.argv or 'filter' in sys.argv)
    
    # Algorithm selection
    alg = sys.argv[2]

    if alg == 'public':
        alg = public_version
    elif alg == 'andrews':
        alg = andrews_version
    elif alg == 'optimised':
        alg = optimised_version
    else:
        raise ValueError('Unknown algorithm.')
    
    # Point cloud
    distribution = triangular
    P = point_cloud(int(sys.argv[3]), distribution=distribution)

    # Mode call
    mode = sys.argv[1]

    if mode == '-t' or mode == 'time':
        print(time_alg(alg, P, filtered=filtered))
    elif mode == '-c' or mode == 'compute':
        print(alg(P, filtered=filtered))
    elif mode == '-p' or mode == 'plot':
        plot_hull(alg(P, filtered=filtered), P)
    else:
        raise ValueError('Unknown mode.')

