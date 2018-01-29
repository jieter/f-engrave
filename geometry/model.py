from time import time
from math import fabs, floor, sqrt
from geometry import *
from util import fmessage


class Model():

    def __init__(self, controller, settings):

        self.controller = controller
        self.settings = settings
        self.init_coords()

        #TODO remove batch flag (use batch | gui)
        self.batch = self.settings.get('batch')
        self.accuracy = self.settings.get('accuracy')

        self.setMaxX(0)
        self.setMinX(0)
        self.setMaxY(0)
        self.setMinY(0)

    def init_coords(self):
        self.coords = []
        self.vcoords = []
        self.init_clean_coords()

    def init_clean_coords(self):
        self.clean_coords = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []
        self.clean_segment = []

    def setMaxX(self, x):
        self.maxX = x

    def setMinX(self, x):
        self.minX = x

    def setMaxY(self, y):
        self.maxY = y

    def setMinY(self, y):
        self.minY = y

    def number_of_clean_segments(self):
        return len(self.clean_segment)

    def number_of_v_segments(self):
        return len(self.vcoords)

    def number_of_segments(self):
        return len(self.coords)

    def get_segments_length(self, i_x1, i_y1, i_x2, i_y2, clean_flag):

        total_length = 0.0

        # determine the total length of segments
        for idx, line in enumerate(self.coords):
            x1 = line[i_x1]
            y1 = line[i_y1]
            x2 = line[i_x2]
            y2 = line[i_y2]
            length = sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )
            if clean_flag == 1:
                if self.clean_segment[idx] != 0:
                    total_length += length
            else:
                total_length += length

        return total_length


    #########################################
    # V-Carve Stuff
    #########################################
    def v_carve(self, v_flop, clean_flag=0, DXF_FLAG=False):

        global STOP_CALC

        #set variable for first point in loop
        xa = 9999
        ya = 9999
        xb = 9999
        yb = 9999
        
        #set variable for the point previously calculated in a loop
        x0 = 9999
        y0 = 9999

        seg_sin0 = 2
        seg_cos0 = 2
        char_num0 = -1
        theta = 9999.0
        loop_cnt = 0 # the number of loops in this model

        if v_flop:
            v_inc = -1
            v_index = self.number_of_segments()
            i_x1 = 2
            i_y1 = 3
            i_x2 = 0
            i_y2 = 1
        else:
            v_inc = 1
            v_index = -1
            i_x1 = 0
            i_y1 = 1
            i_x2 = 2
            i_y2 = 3

        not_b_carve = not bool(self.settings.get('v_pplot') == "BALL")
        v_pplot = self.settings.get('v_pplot')

        CHK_STRING = self.settings.get('v_check_all')
        #TODO is check not set before, else add set check in settings
        if self.settings.get('input_type') != "text":
            CHK_STRING = "all"

        bit_angle = self.settings.get('v_bit_angle')

        #TODO get rid of controller dependency
        #vbit_dia = self.settings.get('v_bit_dia')
        rbit = self.controller.calc_vbit_dia()/2.0

        dline = self.settings.get('v_step_len')
        dangle = degrees(dline/rbit)
        if dangle < 2.0:
            dangle = 2.0
                    
        v_step_corner = self.settings.get('v_step_corner')
        if self.settings.get('inlay'):
            v_drv_corner = 360 - v_step_corner
        else:
            v_drv_corner = float(self.controller.v_drv_corner.get())
                    
        #TODO get rid of controller dependency
        clean_dia = float(self.controller.clean_dia.get())
        r_inlay_top = self.controller.calc_r_inlay_top()
        if clean_flag != 1 :
            rmax = rbit
        else:
            rmax = rbit + clean_dia/2

        midx = (self.maxX+self.minX)/2
        midy = (self.maxY+self.minY)/2
        xLength = self.maxX-self.minX
        yLength = self.maxY-self.minY
        
        #TODO get rid of controller dependency
        cszw = int(self.controller.PreviewCanvas.cget("width"))
        cszh = int(self.controller.PreviewCanvas.cget("height"))
            
        #########################
        # Setup Grid Partitions #
        #########################
        coord_radius = []
        xN = 0
        yN = 0

        xN_minus_1 = max(int(xLength/((2*rmax+dline)*1.1)), 1)
        yN_minus_1 = max(int(yLength/((2*rmax+dline)*1.1)), 1)

        xPartitionLength = xLength/xN_minus_1
        yPartitionLength = yLength/yN_minus_1

        xN = xN_minus_1+1
        yN = yN_minus_1+1

        if xPartitionLength < Zero:
            xPartitionLength = 1
        if yPartitionLength < Zero:
            yPartitionLength = 1
            
        self.xPartitionLength = xPartitionLength
        self.yPartitionLength = yPartitionLength

        self.partitionList = []
        for xCount in range(0, xN):
            self.partitionList.append([])
            for yCount in range(0, yN):
                self.partitionList[xCount].append([])
        ###############################
        # End Setup Grid Partitions   #
        ###############################

        CUR_CNT = -1
        while (self.number_of_segments() > CUR_CNT+1):
            CUR_CNT += 1
            XY_R = self.coords[CUR_CNT][:]
            x1_R = XY_R[0]
            y1_R = XY_R[1]
            x2_R = XY_R[2]
            y2_R = XY_R[3]
            LENGTH = sqrt( (x2_R-x1_R)*(x2_R-x1_R) + (y2_R-y1_R)*(y2_R-y1_R) )
            
            R_R = LENGTH/2 + rmax
            X_R = (x1_R + x2_R)/2
            Y_R = (y1_R + y2_R)/2
            coord_radius.append([X_R, Y_R, R_R])

            #####################################################
            # Determine active partitions for each line segment #
            #####################################################
            coded_index=[]

            ## find the local coordinates of the line segment ends
            x1_G = XY_R[0] - self.minX
            y1_G = XY_R[1] - self.minY
            x2_G = XY_R[2] - self.minX
            y2_G = XY_R[3] - self.minY

            ## Find the grid box index for each line segment end
            X1i = int( x1_G / xPartitionLength )
            X2i = int( x2_G / xPartitionLength )
            Y1i = int( y1_G / yPartitionLength )
            Y2i = int( y2_G / yPartitionLength )

            ## Find the max/min grid box locations
            Xindex_min = min(X1i,X2i)
            Xindex_max = max(X1i,X2i)
            Yindex_min = min(Y1i,Y2i)
            Yindex_max = max(Y1i,Y2i)

            check_points = []
            if Xindex_max > Xindex_min and abs(x2_G-x1_G) > Zero:

                if Yindex_max > Yindex_min and abs(y2_G-y1_G) > Zero:
                    check_points.append([X1i, Y1i])
                    check_points.append([X2i, Y2i])
                    
                    ## Establish line equation variables: y=m*x+b
                    m_G = (y2_G-y1_G)/(x2_G-x1_G)
                    b_G = y1_G - m_G*x1_G

                    ## Add check point in each partition in the range of X values
                    x_ind_check = Xindex_min+1
                    while x_ind_check <= Xindex_max-1:
                        x_val = x_ind_check * xPartitionLength
                        y_val = m_G * x_val + b_G
                        y_ind_check = int(y_val/yPartitionLength)
                        check_points.append([x_ind_check, y_ind_check])
                        x_ind_check = x_ind_check + 1
                        
                    ## Add check point in each partition in the range of Y values
                    y_ind_check = Yindex_min+1
                    while y_ind_check <= Yindex_max-1:
                        y_val =  y_ind_check * yPartitionLength
                        x_val = (y_val-b_G ) / m_G
                        x_ind_check = int(x_val/xPartitionLength)
                        check_points.append([x_ind_check, y_ind_check])
                        y_ind_check = y_ind_check + 1
                else:
                    x_ind_check = Xindex_min
                    y_ind_check = Yindex_min
                    while x_ind_check <= Xindex_max:
                        check_points.append([x_ind_check, y_ind_check])
                        x_ind_check = x_ind_check + 1
            else:
                x_ind_check = Xindex_min
                y_ind_check = Yindex_min
                while y_ind_check <= Yindex_max:
                    check_points.append([x_ind_check, y_ind_check])
                    y_ind_check = y_ind_check + 1

            ## For each grid box in check_points add the grid box and all adjacent grid boxes
            ## to the list of boxes for this line segment
            for xy_point in check_points:
                xy_p = xy_point
                xIndex = xy_p[0]
                yIndex = xy_p[1]
                for i in range( max(xIndex-1,0), min(xN, xIndex+2) ):
                    for j in range( max(yIndex-1,0), min(yN, yIndex+2) ):
                        coded_index.append(int(i+j*xN))

            codedIndexSet = set(coded_index)
            
            for thisCode in codedIndexSet:
                thisIndex = thisCode
                line_R_appended = XY_R
                line_R_appended.append(X_R)
                line_R_appended.append(Y_R)
                line_R_appended.append(R_R)
                self.partitionList[int(thisIndex%xN)][int(thisIndex/xN)].append(line_R_appended)
        #########################################################
        # End Determine active partitions for each line segment #
        #########################################################

        TOT_LENGTH = self.get_segments_length(i_x1, i_y1, i_x2, i_y2, clean_flag)
        MAX_CNT = self.number_of_segments()

        CUR_LENGTH = 0.0
        CUR_CNT = -1
        START_TIME = time()

        #Update canvas with modified paths
        if not self.batch:
            self.controller.plot_data()

        if TOT_LENGTH > 0.0:

            calc_flag = 1

            for line in range( self.number_of_segments() ):

                CUR_CNT += 1

                if clean_flag == 0:
                    self.clean_segment.append(0)
                elif self.number_of_clean_segments() != self.number_of_segments():
                    fmessage("Need to Recalculate V-Carve Path")
                    break
                else:
                    calc_flag = self.clean_segment[CUR_CNT]
                
                CUR_PCT = float(CUR_LENGTH)/TOT_LENGTH*100.0
                if CUR_PCT > 0.0:
                    MIN_REMAIN = ( time()-START_TIME )/60 * (100-CUR_PCT)/CUR_PCT
                    MIN_TOTAL = 100.0/CUR_PCT * ( time()-START_TIME )/60
                else:
                    MIN_REMAIN = -1
                    MIN_TOTAL = -1
                    
                if not self.batch:
                    self.controller.statusMessage.set('%.1f %% ( %.1f Minutes Remaining | %.1f Minutes Total )' %( CUR_PCT, MIN_REMAIN, MIN_TOTAL ) )
                    self.controller.statusbar.configure( bg='yellow' )
                    self.controller.PreviewCanvas.update()

                if STOP_CALC != 0:
                    STOP_CALC=0

                    if clean_flag != 1:
                        self.vcoords = []
                    else:
                        self.clean_coords = []
                        calc_flag = 0
                    break

                v_index = v_index + v_inc
                New_Loop = 0
                x1 = self.coords[v_index][i_x1]
                y1 = self.coords[v_index][i_y1]
                x2 = self.coords[v_index][i_x2]
                y2 = self.coords[v_index][i_y2]
                char_num = int(self.coords[v_index][5])
                dx = x2-x1
                dy = y2-y1
                Lseg = sqrt(dx*dx + dy*dy)

                if Lseg < Zero: #was accuracy
                    continue
                
                #calculate the sin and cos of the coord transformation needed for
                #the distance calculations
                seg_sin = dy/Lseg
                seg_cos = -dx/Lseg
                phi = get_angle(seg_sin, seg_cos)
                
                if calc_flag != 0:
                    CUR_LENGTH = CUR_LENGTH + Lseg
                else:
                    #theta = phi         #V1.62
                    #x0=x2               #V1.62
                    #y0=y2               #V1.62
                    #seg_sin0=seg_sin    #V1.62
                    #seg_cos0=seg_cos    #V1.62
                    #char_num0=char_num  #V1.62
                    continue
                
                if fabs(x1-x0) > Zero or fabs(y1-y0) > Zero or char_num != char_num0:
                #if char_num != char_num0:
                    New_Loop = 1
                    loop_cnt += 1
                    xa = float(x1)
                    ya = float(y1)
                    xb = float(x2)
                    yb = float(y2)
                    theta = 9999.0
                    seg_sin0 = 2
                    seg_cos0 = 2

                if seg_cos0 > 1.0:
                    delta = 180
                else:
                    xtmp1 = (x2-x1) * seg_cos0 - (y2-y1) * seg_sin0
                    ytmp1 = (x2-x1) * seg_sin0 + (y2-y1) * seg_cos0
                    Ltmp = sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                    d_seg_sin = ytmp1/Ltmp
                    d_seg_cos = xtmp1/Ltmp
                    delta = get_angle(d_seg_sin, d_seg_cos)

                if delta < float(v_drv_corner) and bit_angle !=0 and not_b_carve and clean_flag != 1:
                    #drive to corner
                    self.vcoords.append([x1, y1, 0.0, loop_cnt])

                if delta > float(v_step_corner):
                   ###########################
                   #add sub-steps around corner
                   ###########################
                   phisteps = max(floor((delta-180)/dangle), 2)
                   step_phi = (delta-180)/phisteps
                   pcnt = 0
                   while pcnt < phisteps-1:
                       pcnt = pcnt+1
                       sub_phi = radians( -pcnt*step_phi + theta )
                       sub_seg_cos = cos(sub_phi)
                       sub_seg_sin = sin(sub_phi)

                       rout = self.find_max_circle(x1, y1, rmax, char_num, sub_seg_sin, sub_seg_cos, 1, CHK_STRING)

                       xv, yv, rv, clean_seg = self.record_v_carve_data(x1, y1, sub_phi, rout, loop_cnt, clean_flag)

                       self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)

                       if (not self.batch) and v_pplot and clean_flag != 1:
                           self.controller.plot_circle(xv, yv, midx, midy, cszw, cszh, "blue", rv, 0)

                theta = phi
                x0 = x2
                y0 = y2
                seg_sin0 = seg_sin
                seg_cos0 = seg_cos
                char_num0 = char_num

                #Calculate the number of steps then the dx and dy for each step
                #Don't calculate at the joints.
                nsteps = max(floor(Lseg/dline), 2)
                dxpt = dx/nsteps
                dypt = dy/nsteps

                ### This makes sure the first cut start at the begining of the first segment
                cnt = 0
                if New_Loop == 1 and bit_angle !=0 and not_b_carve:
                    cnt = -1

                seg_sin =  dy/Lseg
                seg_cos = -dx/Lseg
                phi2 = radians(get_angle(seg_sin, seg_cos))
                while cnt < nsteps-1:
                    cnt += 1
                    #determine location of next step along outline (xpt, ypt)
                    xpt = x1 + dxpt * cnt
                    ypt = y1 + dypt * cnt

                    rout = self.find_max_circle(xpt, ypt, rmax, char_num, seg_sin, seg_cos, 0, CHK_STRING)
                    # Make the first cut drive down at an angle instead of straight down plunge
                    if cnt == 0 and not_b_carve:
                        rout = 0.0
                    xv, yv, rv, clean_seg = self.record_v_carve_data(xpt, ypt, phi2, rout, loop_cnt, clean_flag)

                    self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)

                    if v_pplot and (not self.batch) and (clean_flag != 1 ):
                        #self.master.update_idletasks()
                        self.controller.update_idletasks()
                        self.controller.plot_circle(xv, yv, midx, midy, cszw, cszh, "blue", rv, 0)

                    if New_Loop == 1 and cnt == 1:
                        xpta = xpt
                        ypta = ypt
                        phi2a = phi2
                        routa = rout

                #################################################
                # Check to see if we need to close an open loop
                #################################################
                if abs(x2-xa) < self.accuracy and abs(y2-ya) < self.accuracy:
                    xtmp1 = (xb-xa) * seg_cos0 - (yb-ya) * seg_sin0
                    ytmp1 = (xb-xa) * seg_sin0 + (yb-ya) * seg_cos0
                    Ltmp = sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                    d_seg_sin = ytmp1/Ltmp
                    d_seg_cos = xtmp1/Ltmp
                    delta = get_angle(d_seg_sin,d_seg_cos)
                    if delta < v_drv_corner and clean_flag != 1:
                        #drive to corner
                        self.vcoords.append([xa, ya, 0.0, loop_cnt])

                    elif delta > v_step_corner:
                        #add substeps around corner
                        phisteps = max(floor((delta-180)/dangle),2)
                        step_phi = (delta-180)/phisteps
                        pcnt = 0

                        while pcnt < phisteps-1:
                            pcnt = pcnt+1
                            sub_phi = radians( -pcnt*step_phi + theta )
                            sub_seg_cos = cos(sub_phi)
                            sub_seg_sin = sin(sub_phi)

                            rout = self.find_max_circle(xa, ya, rmax, char_num, sub_seg_sin, sub_seg_cos, 1, CHK_STRING)
                            xv, yv, rv, clean_seg = self.record_v_carve_data(xa, ya, sub_phi, rout, loop_cnt, clean_flag)
                            self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                            if v_pplot and (not self.batch) and (clean_flag != 1 ):
                                self.controller.plot_circle(xv, yv, midx, midy, cszw, cszh, "blue", rv, 0)

                        xv, yv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, routa, loop_cnt, clean_flag)
                        self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                    else:
                        # Add closing segment
                        xv, yv, rv, clean_seg = self.record_v_carve_data(xpta, ypta, phi2a, routa, loop_cnt, clean_flag)
                        self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)

        # return Done or not                
        if CUR_CNT == MAX_CNT-1:
            return True
        else:
            return False

    def record_v_carve_data(self, x1, y1, phi, rout, loop_cnt, clean_flag):

        #TODO preferences instead of Application
        rbit = self.controller.calc_vbit_dia() / 2.0
        r_clean = float(self.controller.clean_dia.get())/2.0
        
        Lx, Ly = transform(0,rout,-phi)
        xnormv = x1+Lx
        ynormv = y1+Ly
        need_clean = 0

        if int(clean_flag) != 1:
            self.vcoords.append([xnormv, ynormv, rout, loop_cnt]) 
            if abs(rbit-rout) <= Zero:
                need_clean = 1
        else:
            if rout >= rbit:
                self.clean_coords.append([xnormv, ynormv, rout, loop_cnt])

        return xnormv, ynormv, rout, need_clean
               
    ############################################################################
    # Routine finds the maximum radius that can be placed in the position      #
    # xpt,ypt witout interfearing with other line segments (rmin is max R LOL) #
    ############################################################################
    def find_max_circle(self, xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING):

        global Zero
        rtmp = rmin

        xIndex = int((xpt-self.minX)/self.xPartitionLength)
        yIndex = int((ypt-self.minY)/self.yPartitionLength)

        self.coords_check=[]

        R_A = abs(rmin)
        Bcnt = -1

        ############################################################
        # Loop over active partitions for the current line segment #
        ############################################################
        for line_B in self.partitionList[xIndex][yIndex]:
            Bcnt = Bcnt+1
            X_B = line_B[len(line_B)-3]
            Y_B = line_B[len(line_B)-2]
            R_B = line_B[len(line_B)-1]
            GAP = sqrt( (X_B-xpt)*(X_B-xpt) + (Y_B-ypt)*(Y_B-ypt)  )
            if GAP < abs(R_A + R_B):
                self.coords_check.append(line_B)

        for linec in self.coords_check:
            XYc = linec
            xmaxt = max(XYc[0],XYc[2]) + rmin*2
            xmint = min(XYc[0],XYc[2]) - rmin*2
            ymaxt = max(XYc[1],XYc[3]) + rmin*2
            ymint = min(XYc[1],XYc[3]) - rmin*2
            if xpt >= xmint and ypt >= ymint and xpt <= xmaxt and ypt <= ymaxt:
                logic_full = True
            else:
                logic_full = False
                continue

            if CHK_STRING == "chr":
                logic_full = logic_full and (char_num == int(XYc[5]))

            if corner == 1:
                logic_full = logic_full and                                                 \
                             ( (fabs(xpt-XYc[0]) > Zero) or (fabs(ypt-XYc[1]) > Zero) ) and \
                             ( (fabs(xpt-XYc[2]) > Zero) or (fabs(ypt-XYc[3]) > Zero) )

            if logic_full:
                xc1 = (XYc[0]-xpt) * seg_cos - (XYc[1]-ypt) * seg_sin
                yc1 = (XYc[0]-xpt) * seg_sin + (XYc[1]-ypt) * seg_cos
                xc2 = (XYc[2]-xpt) * seg_cos - (XYc[3]-ypt) * seg_sin
                yc2 = (XYc[2]-xpt) * seg_sin + (XYc[3]-ypt) * seg_cos

                if fabs(xc2-xc1) < Zero and fabs(yc2-yc1) > Zero:
                    rtmp = fabs(xc1)
                    if max(yc1,yc2) >= rtmp and min(yc1,yc2) <= rtmp:
                        rmin = min(rmin,rtmp)

                elif fabs(yc2-yc1) < Zero and fabs(xc2-xc1) > Zero:
                    if max(xc1,xc2) >= 0.0 and min(xc1,xc2) <= 0.0 and yc1 > Zero:
                        rtmp = yc1/2.0
                        rmin = min(rmin,rtmp)

                if fabs(yc2-yc1) > Zero and fabs(xc2-xc1) > Zero:
                    m = (yc2-yc1)/(xc2-xc1)
                    b = yc1 - m*xc1
                    sq = m+1/m
                    A = 1 + m*m - 2*m*sq
                    B = -2*b*sq
                    C = -b*b
                    try:
                        sq_root = sqrt(B*B-4*A*C)
                        xq1 = (-B + sq_root)/(2*A)

                        if xq1 >= min(xc1,xc2) and xq1 <= max(xc1,xc2):
                            rtmp = xq1*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)

                        xq2 = (-B - sq_root)/(2*A)
                        yq2 = m*xq2+b

                        if xq2 >= min(xc1,xc2) and xq2 <= max(xc1,xc2):
                            rtmp = xq2*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)
                    except:
                        pass

                if yc1 > Zero:
                    rtmp = (xc1*xc1 + yc1*yc1) / (2*yc1)
                    rmin=min(rmin,rtmp)

                if yc2 > Zero:
                    rtmp = (xc2*xc2 + yc2*yc2) / (2*yc2)
                    rmin = min(rmin,rtmp)

                if abs(yc1) < Zero and abs(xc1) < Zero:
                    if yc2 > Zero:
                        rmin = 0.0
                        
                if abs(yc2) < Zero and abs(xc2) < Zero:
                    if yc1 > Zero:
                        rmin = 0.0

        return rmin
        
    def sort_for_v_carve(self, LN_START=0):
        self.coords = self._sort_for_v_carve(self.coords, LN_START)

    def _sort_for_v_carve(self, sort_coords, LN_START):

        ecoords = []
        Lbeg=[]
        Lend=[]
        cnt=0

        for i in range(len(sort_coords)):
        
            [x1, y1, x2, y2, dummy1, dummy2] = sort_coords[i]

            if i == 0:
                cnt = 0
                ecoords.append([x1, y1])
                Lbeg.append(cnt)
                cnt = cnt+1
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2
            else:
                dist = sqrt((oldx - x1)**2 + (oldy - y1)**2)
                # check and see if we need to move
                # to a new discontinuous start point
                if dist > Zero:
                    Lend.append(cnt)
                    cnt = cnt+1
                    ecoords.append([x1,y1])
                    Lbeg.append(cnt)
                cnt += 1
                ecoords.append([x2, y2])
                oldx, oldy = x2, y2

        Lend.append(cnt)

        if not self.batch:
            self.controller.statusMessage.set('Checking Input Image Data')
            self.controller.master.update()

        ######################################################
        ### Fully Close Closed loops and Remove Open Loops ###
        ######################################################
        i = 0
        LObeg = []
        LOend = []
        while i < len(Lbeg): #for each loop
            [Xstart, Ystart] = ecoords[Lbeg[i]]
            [Xend, Yend] = ecoords[Lend[i]]
            dist = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
            if  dist <= Zero: #if end is the same as the beginning (changed in V1.55: was Acc)
                ecoords[Lend[i]] = [Xstart, Ystart]
                i += 1
            else:  #end != to beginning
                LObeg.append(Lbeg.pop(i))
                LOend.append(Lend.pop(i))

        LNbeg = []
        LNend = []
        LNloop = []
        
        #######################################################
        ###  For Each open loop connect to the next closest ###
        ###  loop end until all of the loops are closed     ###
        #######################################################
        Lcnt = 0
        while len(LObeg) > 0: #for each Open Loop
            Start = LObeg.pop(0)
            End = LOend.pop(0)
            Lcnt += 1
            LNloop.append(Lcnt)
            LNbeg.append(Start)
            LNend.append(End)
            [Xstart, Ystart] = ecoords[Start]

            OPEN = True
            while OPEN == True and len(LObeg) > 0:
                [Xend,Yend] = ecoords[End]
                dist_beg_min = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
                dist_end_min = dist_beg_min
                k_min_beg = -1
                k_min_end = -1
                for k in range(len(LObeg)):
                    [Xkstart, Ykstart] = ecoords[LObeg[k]]
                    [Xkend, Ykend] = ecoords[LOend[k]]
                    dist_beg = sqrt((Xend-Xkstart)**2 + (Yend-Ykstart)**2)
                    dist_end = sqrt((Xend - Xkend)**2 + (Yend - Ykend)**2)
                    if dist_beg < dist_beg_min:
                        dist_beg_min = dist_beg
                        k_min_beg = k
                    if dist_end < dist_end_min:
                        dist_end_min = dist_end
                        k_min_end = k

                if k_min_beg == -1 and k_min_end == -1:
                    kbeg = End
                    kend = Start

                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[Start])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords)-2)
                    LNend.append(len(ecoords)-1)
                    OPEN = False
                elif dist_end_min < dist_beg_min:
                    kend = LObeg.pop(k_min_end)
                    kbeg = LOend.pop(k_min_end)

                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[kbeg])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords)-2)
                    LNend.append(len(ecoords)-1)
                    LNloop.append(Lcnt)
                    LNbeg.append(kbeg)
                    LNend.append(kend)
                    End = kend
                else:
                    kbeg = LObeg.pop(k_min_beg)
                    kend = LOend.pop(k_min_beg)

                    ecoords.append(ecoords[End])
                    ecoords.append(ecoords[kbeg])

                    LNloop.append(Lcnt)
                    LNbeg.append(len(ecoords)-2)
                    LNend.append(len(ecoords)-1)
                    LNloop.append(Lcnt)
                    LNbeg.append(kbeg)
                    LNend.append(kend)
                    End = kend

            if OPEN == True and len(LObeg) == 0:
                ecoords.append(ecoords[End])
                ecoords.append(ecoords[Start])
                LNloop.append(Lcnt)
                LNbeg.append(len(ecoords)-2)
                LNend.append(len(ecoords)-1)

        #######################################################
        ### Make new sequential ecoords for each new loop   ###
        #######################################################
        Loop_last = -1
        for k in range(len(LNbeg)):
            Start = LNbeg[k]
            End = LNend[k]
            Loop = LNloop[k]
            if Loop != Loop_last:
                Lbeg.append(len(ecoords))
                if Loop_last != -1:
                    Lend.append(len(ecoords)-1)
                Loop_last = Loop

            if Start > End:
                step = -1
            else:
                step = 1
            for i in range(Start, End+step, step):
                [x1,y1] = ecoords[i]
                ecoords.append([x1,y1])
        if len(Lbeg) > len(Lend):
            Lend.append(len(ecoords)-1)

        ###########################################
        ###   Determine loop directions CW/CCW  ###
        ###########################################
        if not self.batch:
            self.controller.statusMessage.set('Calculating Initial Loop Directions (CW/CCW)')
            self.controller.master.update()

        Lflip = []
        Lcw = []

        for k in range(len(Lbeg)):
            Start = Lbeg[k]
            End = Lend[k]
            step = 1

            signedArea = 0.0

            [x1,y1] = ecoords[Start]
            for i in range(Start+1,End+step,step):
                [x2,y2] = ecoords[i]
                signedArea += (x2-x1)*(y2+y1)
                x1 = x2
                y1 = y2
            if signedArea > 0.0:
                Lflip.append(False)
                Lcw.append(True)
            else:
                Lflip.append(True)
                Lcw.append(False)

        Nloops = len(Lbeg)
        LoopTree = []
        Lnum = []
        
        for iloop in range(LN_START, Nloops+LN_START):
            LoopTree.append([iloop, [], []])
            Lnum.append(iloop)

        #####################################################
        # For each loop determine if other loops are inside #
        #####################################################
        for iloop in range(Nloops):
            CUR_PCT = float(iloop)/Nloops*100.0
            if not self.batch:
                self.controller.statusMessage.set('Determining Which Side of Loop to Cut: %d of %d' %(iloop+1,Nloops))
                self.controller.master.update()
                
            ipoly = ecoords[Lbeg[iloop]:Lend[iloop]]

            ## Check points in other loops (could just check one) ##
            if ipoly != []:
                for jloop in range(Nloops):
                    if jloop != iloop:
                        inside = 0
                        jval = Lbeg[jloop]
                        inside = inside + point_inside_polygon(ecoords[jval][0],ecoords[jval][1],ipoly)
                        if inside > 0:
                            Lflip[jloop] = not Lflip[jloop]
                            LoopTree[iloop][1].append(jloop)
                            LoopTree[jloop][2].append(iloop)

        #####################################################
        # Set Loop clockwise flag to the state of each loop #
        #####################################################
        # could flip cut side here for auto side determination
        for iloop in range(Nloops):
            if Lflip[iloop]:
                Lcw[iloop] = not Lcw[iloop]

        CUR_PCT = 0.0
        #################################################
        # Find new order based on distance to next beg  #
        #################################################
        if not self.batch:
            self.controller.statusMessage.set('Re-Ordering Loops')
            self.controller.master.update()

        order_out = []
        if len(Lflip) > 0:
            if Lflip[0]:
                order_out.append([ Lend[0], Lbeg[0], Lnum[0] ])
            else:
                order_out.append([ Lbeg[0], Lend[0], Lnum[0] ])

        inext = 0
        total = len(Lbeg)
        for i in range(total-1):
            Lbeg.pop(inext)
            ii = Lend.pop(inext)
            Lflip.pop(inext)
            Lnum.pop(inext)

            Xcur = ecoords[ii][0]
            Ycur = ecoords[ii][1]

            dx = Xcur - ecoords[ Lbeg[0] ][0]
            dy = Ycur - ecoords[ Lbeg[0] ][1]
            min_dist = dx*dx + dy*dy

            inext = 0
            for j in range(1, len(Lbeg)):
                dx = Xcur - ecoords[ Lbeg[j] ][0]
                dy = Ycur - ecoords[ Lbeg[j] ][1]
                dist = dx*dx + dy*dy
                if dist < min_dist:
                    min_dist = dist
                    inext = j

            if Lflip[inext]:
                order_out.append([ Lend[inext], Lbeg[inext], Lnum[inext] ])
            else:
                order_out.append([ Lbeg[inext], Lend[inext], Lnum[inext] ])

        ###########################################################
        temp_coords=[]
        for k in range(len(order_out)):
            [Start, End, LN] = order_out[k]
            if Start > End:
                step = -1
            else:
                step = 1
            xlast = ""
            ylast = ""
            xa,ya = ecoords[Start]
            for i in range(Start+step, End+step, step):
                if xlast != "" and ylast != "":
                    x1 = xlast
                    y1 = ylast
                else:
                    [x1,y1] = ecoords[i-step]
                [x2,y2] = ecoords[i]

                Lseg = sqrt((x2-x1)**2 + (y2-y1)**2)
                if Lseg >= self.accuracy:
                    temp_coords.append([x1,y1,x2,y2,LN,0])
                    xlast = ""
                    ylast = ""
                else:
                    xlast = x1
                    ylast = y1
                    
            if  xlast != "" and  ylast != "":
                Llast = sqrt((x1-xa)*(x1-xa) + (y1-ya)*(y1-ya))
                if len(temp_coords) > 1:
                    if Llast <= self.accuracy and LN == temp_coords[-1][4]:
                        temp_coords[-1][2] = xa
                        temp_coords[-1][3] = ya
                    else:
                        temp_coords.append([x1,y1,xa,ya,LN,0])
        return temp_coords

    def _find_paths(self, check_coords_in, clean_dia, Radjust, clean_step, skip, direction):
        check_coords=[]
        
        if direction == "Y":
            cnt = -1
            for line in check_coords_in:
                cnt += 1
                XY = line
                check_coords.append([XY[1], XY[0], XY[2]])
        else:
            check_coords = check_coords_in

        minx_c = 0
        maxx_c = 0
        miny_c = 0
        maxy_c = 0
        
        if len(check_coords) > 0:
            minx_c = check_coords[0][0]-check_coords[0][2]
            maxx_c = check_coords[0][0]+check_coords[0][2]
            miny_c = check_coords[0][1]-check_coords[0][2]
            maxy_c = check_coords[0][1]+check_coords[0][2]
        for line in check_coords:
            XY = line
            minx_c = min(minx_c, XY[0]-XY[2] )
            maxx_c = max(maxx_c, XY[0]+XY[2] )
            miny_c = min(miny_c, XY[1]-XY[2] )
            maxy_c = max(maxy_c, XY[1]+XY[2] )

        DX = clean_dia*clean_step
        DY = DX
        Xclean_coords = []
        Xclean_coords_short = []

        if direction != "None":
            #########################################################################
            # Find ends of horizontal lines for carving clean-up
            #########################################################################
            loop_cnt = 0
            Y = miny_c
            line_cnt = skip-1
            while Y <= maxy_c:
                line_cnt = line_cnt+1  
                X = minx_c
                x1 = X
                x2 = X
                x1_old = x1
                x2_old = x2

                # Find relevant clean_coord_data
                ################################
                temp_coords=[]
                for line in check_coords:
                    XY=line
                    if Y < XY[1]+XY[2] and Y > XY[1]-XY[2]:
                        temp_coords.append(XY)
                ################################

                while X <= maxx_c:
                    for line in temp_coords:
                        XY = line
                        h = XY[0]
                        k = XY[1]
                        R = XY[2]-Radjust
                        dist = sqrt((X-h)**2 + (Y-k)**2)
                        if dist <= R:
                            Root = sqrt(R**2 - (Y-k)**2)
                            XL = h-Root
                            XR = h+Root
                            if XL < x1:
                                x1 = XL
                            if XR > x2:
                                x2 = XR
                    if x1 == x2:
                        X = X+DX
                        x1 = X
                        x2 = X
                    elif x1 == x1_old and x2 == x2_old:
                        loop_cnt += 1
                        Xclean_coords.append([x1, Y, loop_cnt])
                        Xclean_coords.append([x2, Y, loop_cnt])
                        if line_cnt == skip:
                            Xclean_coords_short.append([x1, Y, loop_cnt])
                            Xclean_coords_short.append([x2, Y, loop_cnt])

                        X = X+DX
                        x1 = X
                        x2 = X
                    else:
                        X = x2
                    x1_old = x1
                    x2_old = x2
                if line_cnt == skip:
                    line_cnt = 0
                Y = Y+DY
            #########################################################################

        if True == False:
            #########################################################################
            # loop over circles recording "pixels" that are covered by the circles
            #########################################################################
            loop_cnt = 0
            Y = miny_c
            while Y <= maxy_c:
                line_cnt = line_cnt+1  
                X = minx_c
                x1 = X
                x2 = X
                x1_old = x1
                x2_old = x2

                # Find relevant clean_coord_data
                ################################
                temp_coords = []
                for line in check_coords:
                    XY = line
                    if Y < XY[1]+XY[2] and Y > XY[1]-XY[2]:
                        temp_coords.append(XY)
                ################################

                while X <= maxx_c:
                    for line in temp_coords:
                        XY = line
                        h = XY[0]
                        k = XY[1]
                        R = XY[2]-Radjust
                        dist = sqrt((X-h)**2 + (Y-k)**2)
                        if dist <= R:
                            Root = sqrt(R**2 - (Y-k)**2)
                            XL = h-Root
                            XR = h+Root
                            if XL < x1:
                                x1 = XL
                            if XR > x2:
                                x2 = XR
                    if x1 == x2:
                        X = X+DX
                        x1 = X
                        x2 = X
                    elif x1 == x1_old and x2 == x2_old:
                        loop_cnt += 1
                        Xclean_coords.append([x1, Y, loop_cnt])
                        Xclean_coords.append([x2, Y, loop_cnt])
                        if line_cnt == skip:
                            Xclean_coords_short.append([x1, Y, loop_cnt])
                            Xclean_coords_short.append([x2, Y, loop_cnt])

                        X = X+DX
                        x1 = X
                        x2 = X
                    else:
                        X = x2
                    x1_old = x1
                    x2_old = x2
                if line_cnt == skip:
                    line_cnt = 0
                Y = Y+DY
            #########################################################################

        Xclean_coords_out = []
        Xclean_coords_short_out = []
        if direction == "Y":

            cnt = -1
            for line in Xclean_coords:
                cnt += 1
                XY = line
                Xclean_coords_out.append([XY[1],XY[0],XY[2]])

            cnt = -1
            for line in Xclean_coords_short:
                cnt += 1
                XY = line
                Xclean_coords_short_out.append([XY[1],XY[0],XY[2]])
        else:
            Xclean_coords_out = Xclean_coords
            Xclean_coords_short_out = Xclean_coords_short

        return Xclean_coords_out, Xclean_coords_short_out

    def _clean_coords_to_path_coords(self, clean_coords_in):
        path_coords_out = []
        # Clean coords format ([xnormv, ynormv, rout, loop_cnt]) - self.clean_coords
        # Path coords format  ([x1,y1,x2,y2,line_cnt,char_cnt])  - self.coords
        for i in range(1, len(clean_coords_in)):
            if clean_coords_in[i][3] == clean_coords_in[i - 1][3]:
                path_coords_out.append([clean_coords_in[i - 1][0],
                                        clean_coords_in[i - 1][1],
                                        clean_coords_in[i][0],
                                        clean_coords_in[i][1],
                                        0,
                                        0])
        return path_coords_out

    def _clean_path_calc(self, bit_type="straight"):

        v_flop = self.get_flop_status(CLEAN_FLAG=True)
        if v_flop:
            edge = 1
        else:
            edge = 0

        loop_cnt = 0
        loop_cnt_out = 0
        #######################################
        # reorganize clean_coords             #
        #######################################
        if bit_type == "straight":
            test_clean = self.clean_P.get() + self.clean_X.get() + self.clean_Y.get()
        else:
            test_clean = self.v_clean_P.get() + self.v_clean_Y.get() + self.v_clean_X.get()

        rbit = self.calc_vbit_dia() / 2.0

        check_coords = []

        self.statusbar.configure(bg='yellow')
        if bit_type == "straight":
            self.controller.statusMessage.set('Calculating Cleanup Cut Paths')
            self.controller.master.update()
            self.clean_coords_sort = []
            clean_dia = float(self.clean_dia.get())  # diameter of cleanup bit
            v_step_len = float(self.v_step_len.get())
            step_over = float(self.clean_step.get())  # percent of cut DIA
            clean_step = step_over / 100.0
            Radjust = clean_dia / 2.0 + rbit
            check_coords = self.clean_coords

        elif bit_type == "v-bit":
            self.controller.statusMessage.set('Calculating V-Bit Cleanup Cut Paths')
            skip = 1
            clean_step = 1.0

            self.master.update()
            self.v_clean_coords_sort = []

            clean_dia = float(self.clean_v.get())  # effective diameter of clean-up v-bit
            if float(clean_dia) < Zero:
                return
            # The next line allows the cutter to get within 1/4 of the
            # v-clean step of the v-carved surface.
            offset = clean_dia / 4.0
            Radjust = rbit + offset
            flat_clean_r = float(self.clean_dia.get()) / 2.0
            for line in self.clean_coords:
                XY = line
                R = XY[2] - Radjust
                if R > 0.0 and R < flat_clean_r - offset - Zero:
                    check_coords.append(XY)

        clean_coords_out = []
        if self.cut_type.get() == "v-carve" and len(self.clean_coords) > 1 and test_clean > 0:
            DX = clean_dia * clean_step
            DY = DX

            if bit_type == "straight":
                MAXD = clean_dia
            else:
                MAXD = sqrt(DX ** 2 + DY ** 2) * 1.1  # fudge factor

            Xclean_coords = []
            Yclean_coords = []
            clean_coords_out = []

            ## NEW STUFF FOR STRAIGHT BIT ##
            if bit_type == "straight":
                MaxLoop = 0
                clean_dia = float(self.clean_dia.get())  # diameter of cleanup bit
                step_over = float(self.clean_step.get())  # percent of cut DIA
                clean_step = step_over / 100.0
                Rperimeter = rbit + (clean_dia / 2.0)

                ###################################################
                # Extract straight bit points from clean_coords
                ###################################################
                check_coords = []
                junk = -1
                for line in self.clean_coords:
                    XY = line
                    R = XY[2]
                    if R >= Rperimeter - Zero:
                        check_coords.append(XY)
                    elif len(check_coords) > 0:
                        junk = junk - 1
                        check_coords.append([None, None, None, junk])
                        # check_coords[len(check_coords)-1][3]=junk

                ###################################################
                # Calculate Straight bit "Perimeter" tool path ####
                ###################################################
                P_coords = []
                loop_coords = self.clean_coords_to_path_coords(check_coords)
                loop_coords = self._sort_for_v_carve(loop_coords, LN_START=0)

                #######################
                # Line fit loop_coords
                #######################
                P_coords = []
                if loop_coords:
                    loop_coords_lin = []
                    cuts = []
                    Ln_last = loop_coords[0][4]
                    for i in range(len(loop_coords)):
                        Ln = loop_coords[i][4]
                        if Ln != Ln_last:
                            for move, (x, y, z), cent in douglas(cuts, tolerance=0.0001, plane=None):
                                P_coords.append([x, y, clean_dia / 2, Ln_last])
                            cuts = []
                        cuts.append([loop_coords[i][0], loop_coords[i][1], 0])
                        cuts.append([loop_coords[i][2], loop_coords[i][3], 0])
                        Ln_last = Ln
                    if cuts:
                        for move, (x, y, z), cent in douglas(cuts, tolerance=0.0001, plane=None):
                            P_coords.append([x, y, clean_dia / 2, Ln_last])
                ##################### 

                loop_coords = self._clean_coords_to_path_coords(P_coords)
                # Find min/max values for x,y and the highest loop number
                x_pmin = 99999
                x_pmax = -99999
                y_pmin = 99999
                y_pmax = -99999
                for i in range(len(P_coords)):
                    MaxLoop = max(MaxLoop, P_coords[i][3])
                    x_pmin = min(x_pmin, P_coords[i][0])
                    x_pmax = max(x_pmax, P_coords[i][0])
                    y_pmin = min(y_pmin, P_coords[i][1])
                    y_pmax = max(y_pmax, P_coords[i][1])
                loop_cnt_out = loop_cnt_out + MaxLoop

                if self.clean_P.get() == 1:
                    clean_coords_out = P_coords

                offset = DX / 2.0
                if self.clean_X.get() == 1:
                    y_pmax = y_pmax - offset
                    y_pmin = y_pmin + offset
                    Ysize = y_pmax - y_pmin
                    Ysteps = ceil(Ysize / (clean_dia * clean_step))
                    if Ysteps > 0:
                        dY = Ysize / Ysteps
                        for iY in range(0, int(Ysteps + 1)):
                            y = y_pmin + iY / Ysteps * (y_pmax - y_pmin)
                            intXYlist = []
                            intXYlist = detect_intersect([x_pmin - 1, y], [x_pmax + 1, y], loop_coords, XY_T_F=True)
                            intXY_len = len(intXYlist)

                            for i in range(edge, intXY_len - 1 - edge, 2):
                                x1 = intXYlist[i][0]
                                y1 = intXYlist[i][1]
                                x2 = intXYlist[i + 1][0]
                                y2 = intXYlist[i + 1][1]
                                if x2 - x1 > offset * 2:
                                    loop_cnt = loop_cnt + 1
                                    Xclean_coords.append([x1 + offset, y1, loop_cnt])
                                    Xclean_coords.append([x2 - offset, y2, loop_cnt])

                if self.clean_Y.get() == 1:
                    x_pmax = x_pmax - offset
                    x_pmin = x_pmin + offset
                    Xsize = x_pmax - x_pmin
                    Xsteps = ceil(Xsize / (clean_dia * clean_step))
                    if Xsteps > 0:
                        dX = Xsize / Xsteps
                        for iX in range(0, int(Xsteps + 1)):
                            x = x_pmin + iX / Xsteps * (x_pmax - x_pmin)
                            intXYlist = []
                            intXYlist = detect_intersect([x, y_pmin - 1], [x, y_pmax + 1], loop_coords, XY_T_F=True)
                            intXY_len = len(intXYlist)
                            for i in range(edge, intXY_len - 1 - edge, 2):
                                x1 = intXYlist[i][0]
                                y1 = intXYlist[i][1]
                                x2 = intXYlist[i + 1][0]
                                y2 = intXYlist[i + 1][1]
                                if y2 - y1 > offset * 2:
                                    loop_cnt = loop_cnt + 1
                                    Yclean_coords.append([x1, y1 + offset, loop_cnt])
                                    Yclean_coords.append([x2, y2 - offset, loop_cnt])
            ## END NEW STUFF FOR STRAIGHT BIT ##

            #######################################
            ## START V-BIT CLEANUP CALCULATIONS  ##
            #######################################
            elif bit_type == "v-bit":

                #########################################################################
                # Find ends of horizontal lines for carving clean-up
                #########################################################################
                Xclean_perimeter, Xclean_coords = self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip,
                                                                   "X")

                #########################################################################
                # Find ends of Vertical lines for carving clean-up
                #########################################################################
                Yclean_perimeter, Yclean_coords = self._find_paths(check_coords, clean_dia, Radjust, clean_step, skip,
                                                                   "Y")

                #######################################################
                # Find new order based on distance                    #
                #######################################################
                if self.v_clean_P.get() == 1:
                    ########################################
                    ecoords = []
                    for line in Xclean_perimeter:
                        XY = line
                        ecoords.append([XY[0], XY[1]])

                    for line in Yclean_perimeter:
                        XY = line
                        ecoords.append([XY[0], XY[1]])

                    ################
                    ###   ends   ###
                    ################
                    Lbeg = []
                    for i in range(1, len(ecoords)):
                        Lbeg.append(i)

                    ########################################
                    order_out = []
                    if len(ecoords) > 0:
                        order_out.append(Lbeg[0])
                    inext = 0
                    total = len(Lbeg)
                    for i in range(total - 1):
                        ii = Lbeg.pop(inext)
                        Xcur = ecoords[ii][0]
                        Ycur = ecoords[ii][1]
                        dx = Xcur - ecoords[Lbeg[0]][0]
                        dy = Ycur - ecoords[Lbeg[0]][1]
                        min_dist = dx * dx + dy * dy

                        inext = 0
                        for j in range(1, len(Lbeg)):
                            dx = Xcur - ecoords[Lbeg[j]][0]
                            dy = Ycur - ecoords[Lbeg[j]][1]
                            dist = dx * dx + dy * dy
                            if dist < min_dist:
                                min_dist = dist
                                inext = j
                        order_out.append(Lbeg[inext])
                    ###########################################################
                    x_start_loop = -8888
                    y_start_loop = -8888
                    x_old = -999
                    y_old = -999
                    for i in order_out:
                        x1 = ecoords[i][0]
                        y1 = ecoords[i][1]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD:
                            dx = x_start_loop - x_old
                            dy = y_start_loop - y_old
                            dist = sqrt(dx * dx + dy * dy)
                            # Fully close loop if the current point is close enough to the start of the loop
                            if dist < MAXD:
                                clean_coords_out.append([x_start_loop, y_start_loop, clean_dia / 2, loop_cnt_out])
                            loop_cnt_out = loop_cnt_out + 1
                            x_start_loop = x1
                            y_start_loop = y1
                        clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])
                        x_old = x1
                        y_old = y1
            #####################################
            ## END V-BIT CLEANUP CALCULATIONS  ##
            #####################################

            ###########################################################
            # Now deal with the horizontal line cuts
            ###########################################################
            if (self.clean_X.get() == 1 and bit_type != "v-bit") or \
                    (self.v_clean_X.get() == 1 and bit_type == "v-bit"):
                x_old = -999
                y_old = -999
                order_out = sort_paths(Xclean_coords)
                loop_old = -1
                for line in order_out:
                    temp = line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1
                    for i in range(temp[0], temp[1] + step, step):
                        x1 = Xclean_coords[i][0]
                        y1 = Xclean_coords[i][1]
                        loop = Xclean_coords[i][2]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD and loop != loop_old:
                            loop_cnt_out = loop_cnt_out + 1
                        clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])
                        x_old = x1
                        y_old = y1
                        loop_old = loop

            ###########################################################
            # Now deal with the vertical line cuts
            ###########################################################
            if (self.clean_Y.get() == 1 and bit_type != "v-bit") or \
                    (self.v_clean_Y.get() == 1 and bit_type == "v-bit"):
                x_old = -999
                y_old = -999
                order_out = sort_paths(Yclean_coords)
                loop_old = -1
                for line in order_out:
                    temp = line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1
                    for i in range(temp[0], temp[1] + step, step):
                        x1 = Yclean_coords[i][0]
                        y1 = Yclean_coords[i][1]
                        loop = Yclean_coords[i][2]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD and loop != loop_old:
                            loop_cnt_out = loop_cnt_out + 1
                        clean_coords_out.append([x1, y1, clean_dia / 2, loop_cnt_out])
                        x_old = x1
                        y_old = y1
                        loop_old = loop

            # TODO move to controller
            self.controller.entry_set(self.controller.Entry_CLEAN_DIA, self.controller.Entry_CLEAN_DIA_Check(), 1)
            self.controller.entry_set(self.controller.Entry_STEP_OVER, self.controller.Entry_STEP_OVER_Check(), 1)
            self.controller.entry_set(self.controller.Entry_V_CLEAN, self.controller.Entry_V_CLEAN_Check(), 1)

            if bit_type == "v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out

        self.controller.statusMessage.set('Done Calculating Cleanup Cut Paths')
        self.controller.statusbar.configure(bg='white')
        self.controller.master.update_idletasks()
