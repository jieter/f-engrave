from math import *


class BSplineClass:

    def __init__(self, degree=0, Knots=[], CPts=[]):
        self.degree = degree
        self.Knots = Knots
        self.CPts = CPts

        self.Knots_len = len(self.Knots)
        self.CPt_len = len(self.CPts[0])
        self.CPts_len = len(self.CPts)

        # Incoming inspection, fit the upper node number, etc.
        if self.Knots_len < self.degree + 1:
            fmessage("SPLINE: degree greater than number of control points.")
        if self.Knots_len != (self.CPts_len + self.degree + 1):
            fmessage("SPLINE: Knot/Control Point/degree number error.")

    # Modified Version of Algorithm A3.2 from "THE NURBS BOOK" pg.93
    def bspline_ders_evaluate(self, n=0, u=0):
        # Calculating the position of the node vector
        span = self.findspan(u)

        # Compute the basis function up to the n th derivative at the point u
        dN = self.ders_basis_functions(span, u, n)

        p = self.degree
        du = min(n, p)

        CK = []
        dPts = []
        for i in range(self.CPt_len):
            dPts.append(0.0)
        for k in range(n + 1):
            CK.append(dPts[:])

        for k in range(du + 1):
            for j in range(p + 1):
                for i in range(self.CPt_len):
                    CK[k][i] += dN[k][j] * self.CPts[span - p + j][i]
        return CK

    # Algorithm A2.1 from "THE NURBS BOOK" pg.68
    def findspan(self, u):
        # Special case when the value is == Endpoint
        if (u == self.Knots[-1]):
            return self.Knots_len - self.degree - 2

        # Binary search
        # (The interval from high to low is always halved by
        # [mid: mi +1] value lies between the interval of Knots)
        low = self.degree
        high = self.Knots_len
        mid = int((low + high) / 2)
        while ((u < self.Knots[mid]) or (u >= self.Knots[mid + 1])):
            if (u < self.Knots[mid]):
                high = mid
            else:
                low = mid
            mid = int((low + high) / 2)
        return mid

    # Algorithm A2.3 from "THE NURBS BOOK" pg.72
    def ders_basis_functions(self, span, u, n):
        d = self.degree

        # Initialize the a matrix
        a = []
        zeile = []
        for j in range(d + 1):
            zeile.append(0.0)
        a.append(zeile[:])
        a.append(zeile[:])

        # Initialize the ndu matrix
        ndu = []
        zeile = []
        for i in range(d + 1):
            zeile.append(0.0)
        for j in range(d + 1):
            ndu.append(zeile[:])

        # Initialize the ders matrix
        ders = []
        zeile = []
        for i in range(d + 1):
            zeile.append(0.0)
        for j in range(n + 1):
            ders.append(zeile[:])

        ndu[0][0] = 1.0
        left = [0]
        right = [0]

        for j in range(1, d + 1):
            left.append(u - self.Knots[span + 1 - j])
            right.append(self.Knots[span + j] - u)
            saved = 0.0
            for r in range(j):
                # Lower Triangle
                ndu[j][r] = right[r + 1] + left[j - r]
                temp = ndu[r][j - 1] / ndu[j][r]
                # Upper Triangle
                ndu[r][j] = saved + right[r + 1] * temp
                saved = left[j - r] * temp
            ndu[j][j] = saved

        # Load the basis functions
        for j in range(d + 1):
            ders[0][j] = ndu[j][d]

        # This section computes the derivatives (Eq. [2.9])
        for r in range(d + 1):  # Loop over function index
            s1 = 0
            s2 = 1  # Alternate rows in array a
            a[0][0] = 1.0
            for k in range(1, n + 1):
                der = 0.0
                rk = r - k
                pk = d - k
                if (r >= k):
                    a[s2][0] = a[s1][0] / ndu[pk + 1][rk]
                    der = a[s2][0] * ndu[rk][pk]
                if (rk >= -1):
                    j1 = 1
                else:
                    j1 = -rk
                if (r - 1 <= pk):
                    j2 = k - 1
                else:
                    j2 = d - r

                # Here he is not in the first derivative of pure
                for j in range(j1, j2 + 1):
                    a[s2][j] = (a[s1][j] - a[s1][j - 1]) / ndu[pk + 1][rk + j]
                    der += a[s2][j] * ndu[rk + j][pk]

                if (r <= pk):
                    a[s2][k] = -a[s1][k - 1] / ndu[pk + 1][r]
                    der += a[s2][k] * ndu[r][pk]

                ders[k][r] = der
                j = s1
                s1 = s2
                s2 = j  # Switch rows

        # Multiply through by the the correct factors
        r = d
        for k in range(1, n + 1):
            for j in range(d + 1):
                ders[k][j] *= r
            r *= (d - k)
        return ders
