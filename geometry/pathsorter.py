def sort_paths(ecoords, i_loop=2):
    """
    Sort paths
    :param ecoords: list of loops
    :param i_loop: inner loop? #TODO
    :return: ordered loops
    """

    # find loop ends
    Lbeg = []
    Lend = []
    if len(ecoords) > 0:
        Lbeg.append(0)
        loop_old = ecoords[0][i_loop]
        for i in range(1, len(ecoords)):
            loop = ecoords[i][i_loop]
            if loop != loop_old:
                Lbeg.append(i)
                Lend.append(i - 1)
            loop_old = loop
        Lend.append(i)

    # Find new order based on distance to next beg or end #
    order_out = []
    use_beg = 0
    if len(ecoords) > 0:
        order_out.append([Lbeg[0], Lend[0]])
    inext = 0
    total = len(Lbeg)
    for i in range(total - 1):
        if use_beg == 1:
            ii = Lbeg.pop(inext)
            Lend.pop(inext)
        else:
            ii = Lend.pop(inext)
            Lbeg.pop(inext)

        Xcur = ecoords[ii][0]
        Ycur = ecoords[ii][1]

        dx = Xcur - ecoords[Lbeg[0]][0]
        dy = Ycur - ecoords[Lbeg[0]][1]
        min_dist = dx * dx + dy * dy

        dxe = Xcur - ecoords[Lend[0]][0]
        dye = Ycur - ecoords[Lend[0]][1]
        min_diste = dxe * dxe + dye * dye

        inext = 0
        inexte = 0
        for j in range(1, len(Lbeg)):
            dx = Xcur - ecoords[Lbeg[j]][0]
            dy = Ycur - ecoords[Lbeg[j]][1]
            dist = dx * dx + dy * dy
            if dist < min_dist:
                min_dist = dist
                inext = j

            dxe = Xcur - ecoords[Lend[j]][0]
            dye = Ycur - ecoords[Lend[j]][1]
            diste = dxe * dxe + dye * dye
            if diste < min_diste:
                min_diste = diste
                inexte = j

        if min_diste < min_dist:
            inext = inexte
            order_out.append([Lend[inexte], Lbeg[inexte]])
            use_beg = 1
        else:
            order_out.append([Lbeg[inext], Lend[inext]])
            use_beg = 0

    return order_out
