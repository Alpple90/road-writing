import numpy as np
import scipy.interpolate as sci

def arcLenghtParameter(pts):
    # Use arclength to obtain positions along a curve, allows for more consistent interpolation.
    # Use those arclength values to parameterise our x and y values e.g. x(t), y(t)
    # Create normalized arclength parameter ->  t E [0, 1] 
    
    # Calculate differences between consecutive points
    diffs = np.diff(pts, axis=0)
    
    # Calculate Euclidean distances between consecutive points
    euclideanDistance = np.linalg.norm(diffs, axis=1)

    # Cumulative sum of distances to get arclength parameterisation. Normalise by total length to get t in [0, 1]
    dists = np.concatenate(([0], np.cumsum(euclideanDistance)))
    return dists / dists[-1]


def interpolate(pts, numPts, method):
    
    #
    points = np.array(pts)
    t = arcLenghtParameter(points)
    t_out = np.linspace(0, 1, numPts)
    
    mask  = np.concatenate([[True], np.diff(t) > 0])
    t, pts = t[mask], points[mask]

    n = len(pts)

    if method == 'linear':
        x_out = np.interp(t_out, t, pts[:, 0])
        y_out = np.interp(t_out, t, pts[:, 1])

    elif method == 'quadratic':
        k     = min(2, n - 1)
        x_out = sci.make_interp_spline(t, pts[:, 0], k=k)(t_out)
        y_out = sci.make_interp_spline(t, pts[:, 1], k=k)(t_out)

    elif method == 'pchip':
        # Piecewise Cubic Hermite — C1, monotone, no overshoot between knots.
        # Well suited to sparse / unevenly spaced road data.
        x_out = sci.PchipInterpolator(t, pts[:, 0])(t_out)
        y_out = sci.PchipInterpolator(t, pts[:, 1])(t_out)

    elif method == 'akima':
        # Akima — C1, locally weighted so single outlier gaps don't propagate.
        # Requires ≥ 3 points; falls back to linear below that.
        if n >= 3:
            x_out = sci.Akima1DInterpolator(t, pts[:, 0])(t_out)
            y_out = sci.Akima1DInterpolator(t, pts[:, 1])(t_out)
        else:
            x_out = np.interp(t_out, t, pts[:, 0])
            y_out = np.interp(t_out, t, pts[:, 1])
            
    elif method == 'cubicspline':
        # C2 natural spline — enforces zero second derivative at endpoints
        if n >= 3:
            x_out = sci.CubicSpline(t, pts[:, 0])(t_out)
            y_out = sci.CubicSpline(t, pts[:, 1])(t_out)
        else:
            x_out = np.interp(t_out, t, pts[:, 0])
            y_out = np.interp(t_out, t, pts[:, 1])

    elif method == 'quartic':
        k     = min(4, n - 1)
        x_out = sci.make_interp_spline(t, pts[:, 0], k=k)(t_out)
        y_out = sci.make_interp_spline(t, pts[:, 1], k=k)(t_out)

    elif method == 'quintic':
        k     = min(5, n - 1)
        x_out = sci.make_interp_spline(t, pts[:, 0], k=k)(t_out)
        y_out = sci.make_interp_spline(t, pts[:, 1], k=k)(t_out)

    elif method == 'smoothing':
        # Does NOT pass through every point — trades fidelity for smoothness
        s = max(1e-6, 0.002 * n)
        if n >= 4:
            x_out = sci.UnivariateSpline(t, pts[:, 0], s=s)(t_out)
            y_out = sci.UnivariateSpline(t, pts[:, 1], s=s)(t_out)
        else:
            x_out = np.interp(t_out, t, pts[:, 0])
            y_out = np.interp(t_out, t, pts[:, 1])
    
    
    return list(zip(x_out, y_out))