from util import MAXINT
from geometry import *


def douglas(st, tolerance=.001, plane=None, _first=True):
    """
    Perform Douglas-Peucker simplification on the path 'st' with the specified
    tolerance.  The '_first' argument is for internal use only.

    The Douglas-Peucker simplification algorithm finds a subset of the input points
    whose path is never more than 'tolerance' away from the original input path.

    If 'plane' is specified as 17, 18, or 19, it may find helical arcs in the given
    plane in addition to lines.

    -- I [scorch] modified the code so the note below does not apply when using plane 17 --
    Note that if there is movement in the plane perpendicular to the arc, it will be distorted,
    so 'plane' should usually be specified only when there is only movement on 2 axes.
    """

    if len(st) == 1:
        yield "G1", st[0], None
        return

    L1 = st[0]
    L2 = st[-1]

    last_point = None
    while (abs(L1[0] - L2[0]) < Zero) \
            and (abs(L1[1] - L2[1]) < Zero) \
            and (abs(L1[2] - L2[2]) < Zero):
        last_point = st.pop()
        try:
            L2 = st[-1]
        except:
            return

    worst_dist = 0
    worst_distz = 0  # added to fix out of plane inaccuracy problem
    worst = 0
    min_rad = MAXINT
    max_arc = -1

    ps = st[0]
    pe = st[-1]

    for i, p in enumerate(st):
        if p is L1 or p is L2:
            continue
        dist = dist_lseg(L1, L2, p)
        distz = dist_lseg(L1, L2, p, z_only=True)  # added to fix out of plane inacuracy problem
        if dist > worst_dist:
            worst = i
            worst_dist = dist
            rad = arc_rad(plane, ps, p, pe)
            if rad < min_rad:
                max_arc = i
                min_rad = rad
        if distz > worst_distz:  # added to fix out of plane inacuracy problem
            worst_distz = distz  # added to fix out of plane inacuracy problem

    worst_arc_dist = 0
    if min_rad != MAXINT:
        c1, c2 = arc_center(plane, ps, st[max_arc], pe)
        Lx, Ly, Lz = st[0]
        if one_quadrant(plane, (c1, c2), ps, st[max_arc], pe):
            for i, (x, y, z) in enumerate(st):
                if plane == 17:
                    dist1 = abs(hypot(c1 - x, c2 - y) - min_rad)
                    dist = sqrt(worst_distz ** 2 + dist1 ** 2)  # added to fix out of plane inaccuracy problem
                elif plane == 18:
                    dist = abs(hypot(c1 - x, c2 - z) - min_rad)
                elif plane == 19:
                    dist = abs(hypot(c1 - y, c2 - z) - min_rad)
                else:
                    dist = MAXINT

                if dist > worst_arc_dist:
                    worst_arc_dist = dist

                mx = (x + Lx) / 2
                my = (y + Ly) / 2
                mz = (z + Lz) / 2
                if plane == 17:
                    dist = abs(hypot(c1 - mx, c2 - my) - min_rad)
                elif plane == 18:
                    dist = abs(hypot(c1 - mx, c2 - mz) - min_rad)
                elif plane == 19:
                    dist = abs(hypot(c1 - my, c2 - mz) - min_rad)
                else:
                    dist = MAXINT
                Lx, Ly, Lz = x, y, z
        else:
            worst_arc_dist = MAXINT
    else:
        worst_arc_dist = MAXINT

    if worst_arc_dist < tolerance and worst_arc_dist < worst_dist:
        ccw = arc_dir(plane, (c1, c2), ps, st[max_arc], pe)
        if plane == 18:
            ccw = not ccw
        yield "G1", ps, None

        if ccw:
            yield "G3", st[-1], arc_fmt(plane, c1, c2, ps)
        else:
            yield "G2", st[-1], arc_fmt(plane, c1, c2, ps)

    elif worst_dist > tolerance:

        if _first:
            yield ("G1", st[0], None)

        for i in douglas(st[:worst + 1], tolerance, plane, False):
            yield i

        yield "G1", st[worst], None

        for i in douglas(st[worst:], tolerance, plane, False):
            yield i
        if _first:
            yield "G1", st[-1], None

    else:
        if _first:
            yield "G1", st[0], None

        if _first:
            yield "G1", st[-1], None

    if last_point is not None:  # added to fix closed loop problem
        yield "G1", st[0], None  # added to fix closed loop problem
