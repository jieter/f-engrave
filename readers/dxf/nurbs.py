from math import *

from bspline import BSplineClass
from elements import PointClass
from geometry import Zero

####################################################
##  Begin Excerpts from dxf2gcode_b02_nurbs_calc  ##
####################################################
class NURBSClass(object):
    def __init__(self, degree=0, Knots=[], Weights=None, CPoints=None):
        self.degree = degree              # Spline degree
        self.Knots = Knots                # Knot Vector
        self.CPoints = CPoints            # Control points of splines [2D]
        self.Weights = Weights            # Weighting of the individual points

        # Initializing calculated variables
        self.HCPts = []                   # Homogeneous points vectors [3D]

        # Convert Points in Homogeneous points
        self.CPts_2_HCPts()

        # Creating the BSplineClass to calculate the homogeneous points
        self.BSpline = BSplineClass(degree=self.degree,
                                    Knots=self.Knots,
                                    CPts=self.HCPts)

    #Calculate a number of evenly distributed points
    def calc_curve_old(self, n=0, cpts_nr=20):
        # Initial values for step and u
        u = 0
        Points = []

        step = self.Knots[-1] / (cpts_nr - 1)
        while u <= self.Knots[-1]:
            Pt = self.NURBS_evaluate(n=n, u=u)
            Points.append(Pt)
            u += step
        return Points


    # Calculate a number points using error limiting
    def calc_curve(self, n=0, tol_deg=20):
        # Initial values for step and u
        u = 0
        Points = []

        tol = radians(tol_deg)
        i = 1
        while self.Knots[i] == 0:
            i = i + 1
        step = self.Knots[i] / 3

        Pt1 = self.NURBS_evaluate(n=n, u=0.0)
        Points.append(Pt1)
        while u<self.Knots[-1]:
            if (u+step > self.Knots[-1]):
                step = self.Knots[-1]-u

            Pt2=self.NURBS_evaluate(n=n,u=u+step)
            Pt_test=self.NURBS_evaluate(n=n,u=u + step/2)

            dx1 = (Pt_test.x - Pt1.x)
            dy1 = (Pt_test.y - Pt1.y)
            L1 = sqrt(dx1*dx1 + dy1*dy1)

            dx2 = (Pt2.x - Pt_test.x)
            dy2 = (Pt2.y - Pt_test.y)
            L2 = sqrt(dx2*dx2 + dy2*dy2)

            if L1 > Zero and L2 > Zero:
                cos_angle = dx1/L1 * dx2/L2 + dy1/L1 * dy2/L2
                if  abs(cos_angle) > 1:
                    cos_angle = int(cos_angle)
                angle=acos(cos_angle)
            else:
                angle=0.0

            if angle > tol:
                step = step/2
            else:
                u+=step
                Points.append(Pt2)
                step = step*2
                Pt1=Pt2
        return Points


    #Calculate a point of NURBS
    def NURBS_evaluate(self,n=0,u=0):

        #Calculate the homogeneous points to the n th derivative
        HPt=self.BSpline.bspline_ders_evaluate(n=n,u=u)

        #Point back to normal coordinates transform
        Point=self.HPt_2_Pt(HPt[0])
        return Point

    #Convert the NURBS control points and weight in a homogeneous vector
    def CPts_2_HCPts(self):
        for P_nr in range(len(self.CPoints)):
            HCPtVec=[self.CPoints[P_nr].x*self.Weights[P_nr],\
                       self.CPoints[P_nr].y*self.Weights[P_nr],\
                       self.Weights[P_nr]]
            self.HCPts.append(HCPtVec[:])

    #Convert a homogeneous vector point in a point
    def HPt_2_Pt(self,HPt):
        return PointClass(x=HPt[0]/HPt[-1],y=HPt[1]/HPt[-1])
