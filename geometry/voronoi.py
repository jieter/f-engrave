import openvoronoi as ovd
from math import (sqrt)
from geometry import Zero

import time


def insert_polygon_points(vd, polygon):
    pts = []
    for p in polygon:
        pts.append(ovd.Point(p[0], p[1]))
    id_list = []
    print("inserting %d point-sites:" % len(pts))
    m = 0
    for p in pts:
        id_list.append(vd.addVertexSite(p))
        # print " ", m, " added vertex ", id_list[len(id_list) - 1]
        m += 1
    return id_list


def insert_polygon_segments(vd, id_list):
    j = 0
    print("inserting %d line-segments:" % len(id_list))
    for n in range(len(id_list)):
        n_nxt = n + 1
        if n == (len(id_list) - 1):
            n_nxt = 0
        # print " ", j, "inserting segment ", id_list[n], " - ", id_list[n_nxt]
        vd.addLineSite(id_list[n], id_list[n_nxt])
        j += 1


def modify_segments(segs):
    segs_mod = []
    for seg in segs:
        first = seg[0]
        last = seg[len(seg) - 1]
        assert (first[0] == last[0] and first[1] == last[1])
        seg.pop()
        seg.reverse()  # to get interior or exterior offsets
        segs_mod.append(seg)
    return segs_mod


def reverse_segments(segs):
    for seg in segs:
        seg.reverse()  # to get interior or exterior offsets
    return


def insert_many_polygons(vd, segs):

    # t_before = time.time()

    polygon_ids = []
    for poly in segs:
        poly_id = insert_polygon_points(vd, poly)
        polygon_ids.append(poly_id)

    # t_after = time.time()
    # pt_time = t_after - t_before
    # t_before = time.time()

    for ids in polygon_ids:
        insert_polygon_segments(vd, ids)

    # t_after = time.time()
    # seg_time = t_after - t_before

    # return [pt_time, seg_time]
    return


def translate(segs, x, y):
    out = []
    for seg in segs:
        seg2 = []
        for p in seg:
            p2 = []
            p2.append(p[0] + x)
            p2.append(p[1] + y)
            seg2.append(p2)
        out.append(seg2)
    return out


def get_loops_from_coords(coords):
    """return a list of loops"""
    loops = []
    segments = []
    next_loop = True
    for segment in coords:
        seg_begin = segment[0:2]
        seg_end = segment[2:4]
        if next_loop:
            first_vertex = seg_begin
            next_loop = False
        segments.append(seg_begin)
        if abs(seg_end[0] - first_vertex[0]) < Zero and abs(seg_end[1] - first_vertex[1]) < Zero:
            loops.append(segments)
            next_loop = True
            segments = []
    return loops


def toolpath_to_v_coords(toolpath):
    v_coords = []
    for loop_cnt, chain in enumerate(toolpath):
        for move in chain:
            for point in move:
                p = point[0]
                z = point[1]
                v_coords.append([p.x, p.y, z, loop_cnt])
    return v_coords


def medial_axis(coords, far=500.0, v_flop=False, clean=False):

    segs = get_loops_from_coords(coords)
    if v_flop:
        reverse_segments(segs)

    n_bins = int(sqrt(len(coords)))  # approx. sqrt(nr of sites)
    vd = ovd.VoronoiDiagram(far, n_bins)
    # vd.debug_on()

    insert_many_polygons(vd, segs)

    print("VD check: %s" % vd.check())

    pi = ovd.PolygonInterior(True)
    vd.filter_graph(pi)
    ma = ovd.MedialAxis()
    vd.filter_graph(ma)

    maw = ovd.MedialAxisWalk(vd.getGraph())
    toolpath = maw.walk()

    return toolpath_to_v_coords(toolpath)
