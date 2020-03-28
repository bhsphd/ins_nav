##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################
from ins_nav.wgs84 import RE, FLATTENING, E2
from math import sqrt, atan2, sin, cos
from ins_nav.utils import RAD2DEG, DEG2RAD
import numpy as np
from collections import namedtuple
from enum import IntFlag

FrameTypes = IntFlag("FrameTypes", "NED ENU")
# NavigationFrame = namedtuple("NavigationFrame", "origin R type")

class NavigationFrame(namedtuple("NavigationFrame", "origin R type")):
    """
    Base local navigation frame class. A user should not call this directly,
    rather derive new frames from it like a Wandering Azimuth frame class.
    """
    __slots__ = ()

    def ecef2nav(self, p_ecef):
        return self.R.dot(p_ecef - self.origin)

    def nav2ecef(self, p_nav):
        r = self.R.T
        return r.dot(p_nav) + self.origin


class ENU(NavigationFrame):
    """
    reference: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU
    """
    __slots__ = ()

    def __new__(cls, o, r):
        return cls.__bases__[0].__new__(cls, o, r, FrameTypes.ENU)

    def __eq__(self, a):
        return self.type == a.type


class NED(NavigationFrame):
    """
    pos_ecef: vector in ECEF to convert
    origin_ecef: origin of local frame in ECEF

    reference: https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
    """
    __slots__ = ()

    def __new__(cls, o, r):
        return cls.__bases__[0].__new__(cls, o, r, FrameTypes.NED)

    def __eq__(self, a):
        return self.type == a.type

    @staticmethod
    def from_ll(lat, lon, alt):
        """
        Creates a local navigation from lat, lon, alt [deg,deg,m]
        """
        o_ecef = llh2ecef(lat, lon, alt)

        lat = DEG2RAD*lat
        lon = DEG2RAD*lon

        R = np.array(
            [
                [-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
                [-np.sin(lon), np.cos(lon), 0],
                [-np.cos(lat)*np.cos(lon), -np.cos(lat)*np.sin(lon), -np.sin(lat)]
            ]
        )

        return NED(o_ecef, R)

    @staticmethod
    def from_ecef(x, y, z):
        """
        Creates a local navigation frame from (x,y,z) [m,m,m] in ECEF frame
        """
        o_ecef = np.array([x,y,z])

        lat, lon, _ = ecef2llh(x,y,z)

        lat = DEG2RAD*lat
        lon = DEG2RAD*lon

        R = np.array(
            [
                [-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
                [-np.sin(lon), np.cos(lon), 0],
                [-np.cos(lat)*np.cos(lon), -np.cos(lat)*np.sin(lon), -np.sin(lat)]
            ]
        )

        return NED(o_ecef, R)



# def ecef2enu():
#     """
#     reference: https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_ECEF_to_ENU
#     """
#     pass
#
# def ecef2ned(pos_ecef, llh_origin):
#     """
#     pos_ecef: vector in ECEF to convert
#     origin_ecef: origin of local frame in ECEF
#
#     reference: https://en.wikipedia.org/wiki/Local_tangent_plane_coordinates
#     """
#
#     lat = DEG2RAD*ned_origin[0]
#     lon = DEG2RAD*ned_origin[1]
#
#     R = np.array(
#         [
#             [-np.sin(lat)*np.cos(lon), -np.sin(lat)*np.sin(lon), np.cos(lat)],
#             [-np.sin(lon), np.cos(lon), 0],
#             [-np.cos(lat)*np.cos(lon), -np.cos(lat)*np.sin(lon), -np.sin(lat)]
#         ]
#     )
#
#     ned_origin_ecef = llh2ecef(ned_origin)
#
#     ned = R.dot(pos_ecef - ned_origin_ecef)
#
#     return ned

# New ------------------------------------------------------------------------------
def ecef2llh(x, y, z):
    """
    ecef: Earth Centered Earth Fixed in [m, m, m]
    llh: latitude, longitude, height (or altitude) in [deg, deg, m]
    """
    p = sqrt(x**2 + y**2)
    b = RE*(1-FLATTENING)
    ep = (RE**2 - b**2)/(b**2)
    theta = atan2(z*RE, p*b)

    l = atan2(y, x)
    L = atan2(z+ep*b*sin(theta)**3, p-E2*RE*cos(theta)**3)
    Re = RE/sqrt(1-E2*sin(L)**2)
    h = p/cos(L) - Re

    L = RAD2DEG * L
    l = RAD2DEG * l
    return np.array([L, l, h])


def llh2ecef(lat, lon, H):
    """
    ecef: Earth Centered Earth Fixed in [m, m, m]
    llh: latitude, longitude, height (or altitude) in [deg, deg, m]

    phi = lat
    lambda = lon
    H = height or altitude
    """
    lat = DEG2RAD * lat
    lon = DEG2RAD * lon
    e2 = E2 # 0.00669437999014
    re = RE # 6378137.0  # m
    rm = re * (1.0 - e2) / pow(1.0 - e2 * sin(lat)**2, 3.0 / 2.0)
    rn = re / sqrt(1.0 - e2 * sin(lat)**2)
    x = (rn + H) * cos(lat) * cos(lon)
    y = (rn + H) * cos(lat) * sin(lon)
    z = (rm + H) * sin(lat)
    return np.array([x, y, z])


def llh2DCM(lat, lon, h, w):
    # lat/lon [rads]
    # h = height [m]
    # w = wander azmuth
    sL = sin(lat)
    cL = cos(lat)
    sl = sin(lon)
    cl = cos(lon)
    Cgn = np.array([[w[1], w[0], 0], [-w[0], w[1], 0], [0, 0, 1]])
    Ceg = np.array([[-sL*cl, -sL*sl, cL], [-sl, cl, 0], [-cL*cl, -cL*sl, -sL]])
    return Cgn.dot(Ceg)

#------------------------------------------------------------------------------------
