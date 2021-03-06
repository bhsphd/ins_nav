##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################

RE = 6378137.0                 # Semi major axis of Earth [m]
model = 'WGS84'
FLATTENING = 0.00335281066475  # 1/298.257223563
E2 = 0.00669437999014          # Eccentricity of Earth ellipsoid squared
RATE = 7.2921157e-5            # Rotation rate of Earth [rad/s]
SF = 1.2383e-3                 # Schuller frequency
MU = 3.986004418e14            # Gravitational parameter of Earth
G0 = 9.7803253359              # Gravity [m/sec^2]
gravity = 9.81                 # Grabity [m/sec^2]

# value?
# class WGS84:
#     re = 6378137.0  # m
#     FLATTENING = 0.00335281066475
#     E2 = 0.00669437999014
