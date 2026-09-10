#Atmosphere model (ISA)
"""
Calculate ISA temperature and pressure at altitude.
altitude: geometric altitude in metres
returns: Ta in Kelvin, Pa in Pascal
"""

import numpy as np

def calculate_atmosphere(altitude):
  T0 = 288.15       # K
  P0 = 101325.0     # Pa
  L = 0.0065        # K/m
  R = 287.05        # J/(kg K)
  g = 9.80665       # m/s^2

  if altitude <= 11000:
      Ta = T0 - L * altitude
      Pa = P0 * (Ta / T0) ** (g / (R * L))
  else:
      Ta = 216.65
      Pa = 22632.06 * np.exp(
          -g * (altitude - 11000) / (R * Ta)
      )

  return Ta, Pa