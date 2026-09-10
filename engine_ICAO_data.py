"""ICAO engine data and comparison helpers.

This module stores ICAO emissions/fuel-flow reference data plus helper mappings
for engine/fan diameter values that can be used when defining engines.

Notes:
- Diameters below are fan diameters where available, since that is the usual
  geometric parameter used in turbofan sizing models.
- Some values are family-level placeholders because publicly available data is
  usually published at engine-family level rather than every exact ICAO variant.
- Duplicate engine rows with same engine name but different BPR/OPR/thrust are
  kept as suffixed keys like "NAME__2".
"""

from copy import deepcopy

# -----------------------------------------------------------------------------
# ICAO master data
# -----------------------------------------------------------------------------
# Structure per engine key:
# {
#   "manufacturer": str,
#   "bpr": float | None,
#   "opr": float | None,
#   "rated_thrust_kN": float | None,
#   "fuel_flow": {"takeoff": ..., "climbout": ..., "approach": ..., "idle": ..., "lto_cycle": ...},
#   "hc_ei": {"takeoff": ..., "climbout": ..., "approach": ..., "idle": ..., "lto_total_g": ...},
#   "co_ei": {"takeoff": ..., "climbout": ..., "approach": ..., "idle": ..., "lto_total_g": ...},
#   "nox_ei": {"takeoff": ..., "climbout": ..., "approach": ..., "idle": ..., "lto_total_g": ...},
# }

icao_data = {
    "PW307A": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 4.2,
        "opr": 20.2,
        "rated_thrust_kN": 28.5,
        "fuel_flow": {"takeoff": 0.329, "climbout": 0.274, "approach": 0.102, "idle": 0.045, "lto_cycle": 144},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 3.24, "lto_total_g": 226},
        "co_ei": {"takeoff": 0.57, "climbout": 0.72, "approach": 3.37, "idle": 39.6, "lto_total_g": 2878},
        "nox_ei": {"takeoff": 15.82, "climbout": 13.67, "approach": 6.78, "idle": 2.39, "lto_total_g": 1045},
    },
    "PW4062": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 4.6,
        "opr": 31.0,
        "rated_thrust_kN": 275.8,
        "fuel_flow": {"takeoff": 2.725, "climbout": 2.125, "approach": 0.718, "idle": 0.210, "lto_cycle": 894},
        "hc_ei": {"takeoff": 0.08, "climbout": 0.07, "approach": 0.09, "idle": 10.86, "lto_total_g": 3594},
        "co_ei": {"takeoff": 0.61, "climbout": 0.50, "approach": 1.93, "idle": 42.61, "lto_total_g": 14475},
        "nox_ei": {"takeoff": 34.36, "climbout": 25.98, "approach": 12.17, "idle": 3.78, "lto_total_g": 14555},
    },
    "PW4x62": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 4.6,
        "opr": 31.9,
        "rated_thrust_kN": 275.8,
        "fuel_flow": {"takeoff": 2.767, "climbout": 2.166, "approach": 0.708, "idle": 0.223, "lto_cycle": 920},
        "hc_ei": {"takeoff": 0.08, "climbout": 0.08, "approach": 0.15, "idle": 3.26, "lto_total_g": 1192},
        "co_ei": {"takeoff": 0.38, "climbout": 0.51, "approach": 1.68, "idle": 23.96, "lto_total_g": 8811},
        "nox_ei": {"takeoff": 37.65, "climbout": 27.55, "approach": 12.78, "idle": 4.14, "lto_total_g": 15864},
    },
    "CF34-8E5A2HA": {
        "manufacturer": "General Electric Company",
        "bpr": 4.7,
        "opr": 25.4,
        "rated_thrust_kN": 64.5,
        "fuel_flow": {"takeoff": 0.721, "climbout": 0.588, "approach": 0.196, "idle": 0.067, "lto_cycle": 260},
        "hc_ei": {"takeoff": 0.01, "climbout": 0.01, "approach": 0.03, "idle": 0.12, "lto_total_g": 15},
        "co_ei": {"takeoff": 0.99, "climbout": 0.82, "approach": 4.35, "idle": 20.21, "lto_total_g": 2417},
        "nox_ei": {"takeoff": 16.37, "climbout": 13.16, "approach": 10.00, "idle": 4.84, "lto_total_g": 2493},
    },
    "CF34-8E5": {
        "manufacturer": "General Electric Company",
        "bpr": 4.7,
        "opr": 23.8,
        "rated_thrust_kN": 59.7,
        "fuel_flow": {"takeoff": 0.652, "climbout": 0.536, "approach": 0.182, "idle": 0.065, "lto_cycle": 243},
        "hc_ei": {"takeoff": 0.01, "climbout": 0.01, "approach": 0.04, "idle": 0.15, "lto_total_g": 17},
        "co_ei": {"takeoff": 0.88, "climbout": 0.81, "approach": 4.66, "idle": 22.47, "lto_total_g": 2571},
        "nox_ei": {"takeoff": 14.55, "climbout": 12.17, "approach": 9.79, "idle": 4.59, "lto_total_g": 2153},
    },
    "D-436-148 F1": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 4.9,
        "opr": 19.8,
        "rated_thrust_kN": 64.4,
        "fuel_flow": {"takeoff": 0.548, "climbout": 0.468, "approach": 0.218, "idle": 0.093, "lto_cycle": 260},
        "hc_ei": {"takeoff": 0.10, "climbout": 0.04, "approach": 0.07, "idle": 2.26, "lto_total_g": None},
        "co_ei": {"takeoff": 0.54, "climbout": 0.54, "approach": 2.99, "idle": 23.46, "lto_total_g": None},
        "nox_ei": {"takeoff": 18.93, "climbout": 16.00, "approach": 7.26, "idle": 3.64, "lto_total_g": None},
    },
    "D-436-148 F2": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 4.9,
        "opr": 20.7,
        "rated_thrust_kN": 68.7,
        "fuel_flow": {"takeoff": 0.581, "climbout": 0.493, "approach": 0.225, "idle": 0.099, "lto_cycle": 274},
        "hc_ei": {"takeoff": 0.09, "climbout": 0.05, "approach": 0.08, "idle": 1.39, "lto_total_g": None},
        "co_ei": {"takeoff": 0.48, "climbout": 0.40, "approach": 2.71, "idle": 19.56, "lto_total_g": None},
        "nox_ei": {"takeoff": 19.76, "climbout": 16.64, "approach": 7.31, "idle": 3.78, "lto_total_g": None},
    },
    "CF6-80C2B5F/B6F/B7F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.0,
        "opr": 32.7,
        "rated_thrust_kN": 267.0,
        "fuel_flow": {"takeoff": 2.569, "climbout": 2.074, "approach": 0.671, "idle": 0.196, "lto_cycle": 848},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.05, "approach": 0.10, "idle": 1.73, "lto_total_g": 562},
        "co_ei": {"takeoff": 0.16, "climbout": 0.13, "approach": 2.02, "idle": 19.32, "lto_total_g": 6285},
        "nox_ei": {"takeoff": 26.61, "climbout": 19.96, "approach": 11.39, "idle": 4.08, "lto_total_g": 11420},
    },
    "D-36 ser. 4A": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 5.0,
        "opr": 19.9,
        "rated_thrust_kN": 63.8,
        "fuel_flow": {"takeoff": 0.634, "climbout": 0.533, "approach": 0.211, "idle": 0.092, "lto_cycle": 265},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 5.4, "lto_total_g": None},
        "co_ei": {"takeoff": 0.5, "climbout": 0.4, "approach": 2.7, "idle": 20.7, "lto_total_g": None},
        "nox_ei": {"takeoff": 26.0, "climbout": 22.0, "approach": 9.0, "idle": 5.5, "lto_total_g": None},
    },
    "CFM56-7B26E": {
        "manufacturer": "CFM International",
        "bpr": 5.1,
        "opr": 27.7,
        "rated_thrust_kN": 117.0,
        "fuel_flow": {"takeoff": 1.213, "climbout": 0.986, "approach": 0.331, "idle": 0.108, "lto_cycle": 429},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.05, "idle": 1.75, "lto_total_g": 302},
        "co_ei": {"takeoff": 0.2, "climbout": 0.16, "approach": 3.07, "idle": 30.94, "lto_total_g": 5476},
        "nox_ei": {"takeoff": 21.79, "climbout": 17.08, "approach": 8.93, "idle": 4.27, "lto_total_g": 4762},
    },
    "CFM56-7B27AE": {
        "manufacturer": "CFM International",
        "bpr": 5.1,
        "opr": 29.0,
        "rated_thrust_kN": 121.4,
        "fuel_flow": {"takeoff": 1.293, "climbout": 1.031, "approach": 0.343, "idle": 0.110, "lto_cycle": 444},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.05, "idle": 1.54, "lto_total_g": 273},
        "co_ei": {"takeoff": 0.31, "climbout": 0.17, "approach": 2.82, "idle": 29.39, "lto_total_g": 5320},
        "nox_ei": {"takeoff": 23.94, "climbout": 17.89, "approach": 9.09, "idle": 4.36, "lto_total_g": 5231},
    },
    "CF6-80C2B5F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 32.8,
        "rated_thrust_kN": 272.5,
        "fuel_flow": {"takeoff": 2.685, "climbout": 2.162, "approach": 0.697, "idle": 0.206, "lto_cycle": 887},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.05, "approach": 0.11, "idle": 1.31, "lto_total_g": 459},
        "co_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 1.83, "idle": 17.45, "lto_total_g": 5931},
        "nox_ei": {"takeoff": 28.58, "climbout": 21.76, "approach": 12.74, "idle": 4.91, "lto_total_g": 13142},
    },
    "CF6-80C2B1F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 30.1,
        "rated_thrust_kN": 254.3,
        "fuel_flow": {"takeoff": 2.422, "climbout": 1.983, "approach": 0.650, "idle": 0.199, "lto_cycle": 830},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.05, "approach": 0.11, "idle": 1.54, "lto_total_g": 513},
        "co_ei": {"takeoff": 0.04, "climbout": 0.04, "approach": 2.13, "idle": 19.23, "lto_total_g": 6317},
        "nox_ei": {"takeoff": 24.94, "climbout": 19.72, "approach": 12.47, "idle": 4.73, "lto_total_g": 11113},
    },
    "CF6-80C2B6F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 31.7,
        "rated_thrust_kN": 267.0,
        "fuel_flow": {"takeoff": 2.594, "climbout": 2.104, "approach": 0.682, "idle": 0.203, "lto_cycle": 867},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.05, "approach": 0.11, "idle": 1.43, "lto_total_g": 490},
        "co_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 1.93, "idle": 18.42, "lto_total_g": 6166},
        "nox_ei": {"takeoff": 27.38, "climbout": 21.05, "approach": 12.63, "idle": 4.81, "lto_total_g": 12420},
    },
    "CF6-80C2B1F__2": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 31.0,
        "rated_thrust_kN": 254.3,
        "fuel_flow": {"takeoff": 2.397, "climbout": 1.953, "approach": 0.639, "idle": 0.190, "lto_cycle": 809},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.05, "approach": 0.10, "idle": 2.00, "lto_total_g": 625},
        "co_ei": {"takeoff": 0.15, "climbout": 0.13, "approach": 2.21, "idle": 20.86, "lto_total_g": 6574},
        "nox_ei": {"takeoff": 24.31, "climbout": 18.58, "approach": 11.24, "idle": 3.97, "lto_total_g": 10139},
    },
    "CF34-8C5": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.1,
        "rated_thrust_kN": 59.4,
        "fuel_flow": {"takeoff": 0.648, "climbout": 0.530, "approach": 0.179, "idle": 0.064, "lto_cycle": 240},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.13, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.64, "climbout": 0.57, "approach": 4.24, "idle": 18.25, "lto_total_g": 2071},
        "nox_ei": {"takeoff": 14.69, "climbout": 12.6, "approach": 10.75, "idle": 4.6, "lto_total_g": 2205},
    },
    "CF34-8C5A1": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.5,
        "rated_thrust_kN": 60.6,
        "fuel_flow": {"takeoff": 0.665, "climbout": 0.543, "approach": 0.183, "idle": 0.065, "lto_cycle": 245},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.13, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.66, "climbout": 0.57, "approach": 4.17, "idle": 17.85, "lto_total_g": 2051},
        "nox_ei": {"takeoff": 15.09, "climbout": 12.82, "approach": 10.87, "idle": 4.65, "lto_total_g": 2287},
    },
    "CF34-8C5A2": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 24.1,
        "rated_thrust_kN": 62.5,
        "fuel_flow": {"takeoff": 0.691, "climbout": 0.563, "approach": 0.188, "idle": 0.066, "lto_cycle": 251},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.13, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.71, "climbout": 0.57, "approach": 4.05, "idle": 17.3, "lto_total_g": 2026},
        "nox_ei": {"takeoff": 15.81, "climbout": 13.15, "approach": 11.06, "idle": 4.7, "lto_total_g": 2419},
    },
    "CF34-8C5A3": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 24.8,
        "rated_thrust_kN": 64.5,
        "fuel_flow": {"takeoff": 0.721, "climbout": 0.586, "approach": 0.193, "idle": 0.067, "lto_cycle": 259},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.12, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.77, "climbout": 0.57, "approach": 3.92, "idle": 16.71, "lto_total_g": 1999},
        "nox_ei": {"takeoff": 16.71, "climbout": 13.52, "approach": 11.09, "idle": 4.76, "lto_total_g": 2565},
    },
    "CF34-8C5B1": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 22.1,
        "rated_thrust_kN": 56.4,
        "fuel_flow": {"takeoff": 0.606, "climbout": 0.497, "approach": 0.171, "idle": 0.063, "lto_cycle": 230},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.07, "idle": 0.16, "lto_total_g": 20},
        "co_ei": {"takeoff": 0.6, "climbout": 0.58, "approach": 4.44, "idle": 19.52, "lto_total_g": 2142},
        "nox_ei": {"takeoff": 13.89, "climbout": 12.03, "approach": 10.42, "idle": 4.5, "lto_total_g": 2010},
    },
    "CF34-8E5__2": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.2,
        "rated_thrust_kN": 59.7,
        "fuel_flow": {"takeoff": 0.652, "climbout": 0.533, "approach": 0.180, "idle": 0.064, "lto_cycle": 241},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.13, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.64, "climbout": 0.57, "approach": 4.23, "idle": 18.16, "lto_total_g": 2066},
        "nox_ei": {"takeoff": 14.77, "climbout": 12.65, "approach": 10.77, "idle": 4.61, "lto_total_g": 2223},
    },
    "CF34-8E5A1": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 24.1,
        "rated_thrust_kN": 62.5,
        "fuel_flow": {"takeoff": 0.691, "climbout": 0.563, "approach": 0.188, "idle": 0.066, "lto_cycle": 251},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.06, "idle": 0.13, "lto_total_g": 18},
        "co_ei": {"takeoff": 0.71, "climbout": 0.57, "approach": 4.05, "idle": 17.3, "lto_total_g": 2026},
        "nox_ei": {"takeoff": 15.81, "climbout": 13.15, "approach": 11.06, "idle": 4.7, "lto_total_g": 2419},
    },
    "CFM56-7B22E": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 24.2,
        "rated_thrust_kN": 101.0,
        "fuel_flow": {"takeoff": 1.004, "climbout": 0.832, "approach": 0.291, "idle": 0.099, "lto_cycle": 376},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.07, "idle": 2.83, "lto_total_g": 446},
        "co_ei": {"takeoff": 0.16, "climbout": 0.17, "approach": 4.18, "idle": 37.9, "lto_total_g": 6179},
        "nox_ei": {"takeoff": 17.4, "climbout": 14.67, "approach": 8.35, "idle": 3.95, "lto_total_g": 3538},
    },
    "CFM56-7B22E/B1": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 24.2,
        "rated_thrust_kN": 101.0,
        "fuel_flow": {"takeoff": 1.004, "climbout": 0.832, "approach": 0.291, "idle": 0.099, "lto_cycle": 376},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.07, "idle": 2.83, "lto_total_g": 446},
        "co_ei": {"takeoff": 0.16, "climbout": 0.17, "approach": 4.18, "idle": 37.9, "lto_total_g": 6179},
        "nox_ei": {"takeoff": 17.4, "climbout": 14.67, "approach": 8.35, "idle": 3.95, "lto_total_g": 3538},
    },
    "CFM56-7B24E": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 25.6,
        "rated_thrust_kN": 107.6,
        "fuel_flow": {"takeoff": 1.086, "climbout": 0.895, "approach": 0.308, "idle": 0.103, "lto_cycle": 398},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.06, "idle": 2.3, "lto_total_g": 377},
        "co_ei": {"takeoff": 0.18, "climbout": 0.15, "approach": 3.68, "idle": 34.71, "lto_total_g": 5854},
        "nox_ei": {"takeoff": 18.93, "climbout": 15.6, "approach": 8.6, "idle": 4.09, "lto_total_g": 3996},
    },
    "CFM56-5B3/3": {
        "manufacturer": "CFM International",
        "bpr": 5.4,
        "opr": 32.6,
        "rated_thrust_kN": 142.3,
        "fuel_flow": {"takeoff": 1.462, "climbout": 1.153, "approach": 0.369, "idle": 0.113, "lto_cycle": 478},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.02, "approach": 0.05, "idle": 1.1, "lto_total_g": 204},
        "co_ei": {"takeoff": 0.54, "climbout": 0.25, "approach": 2.14, "idle": 25.59, "lto_total_g": 4765},
        "nox_ei": {"takeoff": 30.9, "climbout": 21.83, "approach": 9.56, "idle": 4.6, "lto_total_g": 6875},
    },
    "CFM56-5B1/3": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 30.2,
        "rated_thrust_kN": 133.4,
        "fuel_flow": {"takeoff": 1.318, "climbout": 1.063, "approach": 0.347, "idle": 0.109, "lto_cycle": 448},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.05, "idle": 1.37, "lto_total_g": 240},
        "co_ei": {"takeoff": 0.38, "climbout": 0.2, "approach": 2.53, "idle": 27.92, "lto_total_g": 4984},
        "nox_ei": {"takeoff": 26.18, "climbout": 19.77, "approach": 9.28, "idle": 4.45, "lto_total_g": 5749},
    },
    "CFM56-5B2/3": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 31.3,
        "rated_thrust_kN": 137.9,
        "fuel_flow": {"takeoff": 1.385, "climbout": 1.107, "approach": 0.358, "idle": 0.111, "lto_cycle": 463},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.02, "approach": 0.05, "idle": 1.22, "lto_total_g": 221},
        "co_ei": {"takeoff": 0.45, "climbout": 0.23, "approach": 2.33, "idle": 26.72, "lto_total_g": 4870},
        "nox_ei": {"takeoff": 28.26, "climbout": 20.76, "approach": 9.42, "idle": 4.53, "lto_total_g": 6268},
    },
    "CFM56-7B20E": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 22.4,
        "rated_thrust_kN": 91.6,
        "fuel_flow": {"takeoff": 0.896, "climbout": 0.746, "approach": 0.268, "idle": 0.094, "lto_cycle": 348},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.08, "idle": 3.84, "lto_total_g": 572},
        "co_ei": {"takeoff": 0.15, "climbout": 0.23, "approach": 5.03, "idle": 43.31, "lto_total_g": 6729},
        "nox_ei": {"takeoff": 15.61, "climbout": 13.5, "approach": 8.0, "idle": 3.8, "lto_total_g": 2987},
    },
    "CF34-10A16/B/C/D": {
        "manufacturer": "General Electric Company",
        "bpr": 5.6,
        "opr": 24.8,
        "rated_thrust_kN": 77.0,
        "fuel_flow": {"takeoff": 0.771, "climbout": 0.638, "approach": 0.216, "idle": 0.085, "lto_cycle": 302},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.04, "idle": 4.71, "lto_total_g": 632},
        "co_ei": {"takeoff": 0.63, "climbout": 0.56, "approach": 4.19, "idle": 47.02, "lto_total_g": 6546},
        "nox_ei": {"takeoff": 18.17, "climbout": 15.18, "approach": 7.91, "idle": 3.66, "lto_total_g": 2763},
    },
    "PW815GA": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 5.6,
        "opr": 35.0,
        "rated_thrust_kN": 71.2,
        "fuel_flow": {"takeoff": 0.699, "climbout": 0.573, "approach": 0.201, "idle": 0.071, "lto_cycle": 264},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.02, "idle": 0.05, "lto_total_g": 7},
        "co_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 1.5, "idle": 13.4, "lto_total_g": 1557},
        "nox_ei": {"takeoff": 24.88, "climbout": 18.89, "approach": 11.47, "idle": 6.41, "lto_total_g": 3422},
    },
    "PW814GA": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 5.7,
        "opr": 33.9,
        "rated_thrust_kN": 68.6,
        "fuel_flow": {"takeoff": 0.667, "climbout": 0.549, "approach": 0.194, "idle": 0.070, "lto_cycle": 256},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.02, "idle": 0.05, "lto_total_g": 6},
        "co_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 1.76, "idle": 13.88, "lto_total_g": 1598},
        "nox_ei": {"takeoff": 23.26, "climbout": 17.94, "approach": 11.46, "idle": 6.25, "lto_total_g": 3168},
    },
    "CFM56-5B4/3": {
        "manufacturer": "CFM International",
        "bpr": 5.7,
        "opr": 27.3,
        "rated_thrust_kN": 120.1,
        "fuel_flow": {"takeoff": 1.142, "climbout": 0.939, "approach": 0.316, "idle": 0.102, "lto_cycle": 407},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.05, "idle": 1.92, "lto_total_g": 314},
        "co_ei": {"takeoff": 0.25, "climbout": 0.16, "approach": 3.24, "idle": 32.07, "lto_total_g": 5386},
        "nox_ei": {"takeoff": 21.57, "climbout": 17.23, "approach": 8.85, "idle": 4.22, "lto_total_g": 4511},
    },
    "CFM56-5B7/3": {
        "manufacturer": "CFM International",
        "bpr": 5.7,
        "opr": 27.3,
        "rated_thrust_kN": 120.1,
        "fuel_flow": {"takeoff": 1.142, "climbout": 0.939, "approach": 0.316, "idle": 0.102, "lto_cycle": 407},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.05, "idle": 1.92, "lto_total_g": 314},
        "co_ei": {"takeoff": 0.25, "climbout": 0.16, "approach": 3.24, "idle": 32.07, "lto_total_g": 5386},
        "nox_ei": {"takeoff": 21.57, "climbout": 17.23, "approach": 8.85, "idle": 4.22, "lto_total_g": 4511},
    },
    "CF34-10A16": {
        "manufacturer": "General Electric Company",
        "bpr": 5.7,
        "opr": 25.1,
        "rated_thrust_kN": 76.9,
        "fuel_flow": {"takeoff": 0.765, "climbout": 0.632, "approach": 0.219, "idle": 0.083, "lto_cycle": 298},
        "hc_ei": {"takeoff": 0.06, "climbout": 0.08, "approach": 0.14, "idle": 6.96, "lto_total_g": 919},
        "co_ei": {"takeoff": 0.49, "climbout": 0.34, "approach": 3.98, "idle": 52.05, "lto_total_g": 7014},
        "nox_ei": {"takeoff": 17.87, "climbout": 15.04, "approach": 7.97, "idle": 3.45, "lto_total_g": 2696},
    },
    "CF34-10A16/16-B": {
        "manufacturer": "General Electric Company",
        "bpr": 5.7,
        "opr": 25.1,
        "rated_thrust_kN": 76.9,
        "fuel_flow": {"takeoff": 0.765, "climbout": 0.632, "approach": 0.219, "idle": 0.083, "lto_cycle": 298},
        "hc_ei": {"takeoff": 0.06, "climbout": 0.08, "approach": 0.14, "idle": 6.96, "lto_total_g": 919},
        "co_ei": {"takeoff": 0.49, "climbout": 0.34, "approach": 3.98, "idle": 52.05, "lto_total_g": 7014},
        "nox_ei": {"takeoff": 17.87, "climbout": 15.04, "approach": 7.97, "idle": 3.45, "lto_total_g": 2696},
    },
    "CFM56-5B6/3": {
        "manufacturer": "CFM International",
        "bpr": 5.9,
        "opr": 24.3,
        "rated_thrust_kN": 104.5,
        "fuel_flow": {"takeoff": 0.965, "climbout": 0.800, "approach": 0.279, "idle": 0.095, "lto_cycle": 361},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.07, "idle": 2.93, "lto_total_g": 440},
        "co_ei": {"takeoff": 0.17, "climbout": 0.17, "approach": 4.35, "idle": 38.39, "lto_total_g": 5912},
        "nox_ei": {"takeoff": 17.73, "climbout": 14.88, "approach": 8.29, "idle": 3.94, "lto_total_g": 3363},
    },
    "CFM56-5B9/3": {
        "manufacturer": "CFM International",
        "bpr": 5.9,
        "opr": 24.2,
        "rated_thrust_kN": 103.6,
        "fuel_flow": {"takeoff": 0.956, "climbout": 0.793, "approach": 0.278, "idle": 0.095, "lto_cycle": 359},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.03, "approach": 0.07, "idle": 3.01, "lto_total_g": 452},
        "co_ei": {"takeoff": 0.16, "climbout": 0.17, "approach": 4.42, "idle": 38.8, "lto_total_g": 6047},
        "nox_ei": {"takeoff": 17.54, "climbout": 14.76, "approach": 8.26, "idle": 3.92, "lto_total_g": 3377},
    },
    "CFM56-5B5/3": {
        "manufacturer": "CFM International",
        "bpr": 6.0,
        "opr": 23.1,
        "rated_thrust_kN": 97.9,
        "fuel_flow": {"takeoff": 0.894, "climbout": 0.743, "approach": 0.264, "idle": 0.092, "lto_cycle": 343},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.08, "idle": 3.55, "lto_total_g": 520},
        "co_ei": {"takeoff": 0.15, "climbout": 0.2, "approach": 4.94, "idle": 41.77, "lto_total_g": 6343},
        "nox_ei": {"takeoff": 16.42, "climbout": 14.01, "approach": 8.03, "idle": 3.81, "lto_total_g": 3047},
    },
    "CFM56-5B8/3": {
        "manufacturer": "CFM International",
        "bpr": 6.0,
        "opr": 22.7,
        "rated_thrust_kN": 96.1,
        "fuel_flow": {"takeoff": 0.875, "climbout": 0.727, "approach": 0.260, "idle": 0.091, "lto_cycle": 338},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.08, "idle": 3.76, "lto_total_g": 544},
        "co_ei": {"takeoff": 0.15, "climbout": 0.21, "approach": 5.12, "idle": 42.82, "lto_total_g": 6448},
        "nox_ei": {"takeoff": 16.1, "climbout": 13.79, "approach": 7.96, "idle": 3.77, "lto_total_g": 2950},
    },
    "CF34-3B": {
        "manufacturer": "General Electric Company",
        "bpr": 6.3,
        "opr": 19.3,
        "rated_thrust_kN": 41.0,
        "fuel_flow": {"takeoff": 0.399, "climbout": 0.329, "approach": 0.116, "idle": 0.049, "lto_cycle": 164},
        "hc_ei": {"takeoff": 0.06, "climbout": 0.05, "approach": 0.13, "idle": 4.69, "lto_total_g": 366},
        "co_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 1.88, "idle": 47.59, "lto_total_g": 3683},
        "nox_ei": {"takeoff": 11.28, "climbout": 9.68, "approach": 6.63, "idle": 3.72, "lto_total_g": 1078},
    },
    "GE90-115B": {
        "manufacturer": "General Electric Company",
        "bpr": 7.0,
        "opr": 43.2,
        "rated_thrust_kN": 513.9,
        "fuel_flow": {"takeoff": 4.594, "climbout": 3.562, "approach": 1.069, "idle": 0.339, "lto_cycle": 1449},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.03, "approach": 0.03, "idle": 5.88, "lto_total_g": 3141},
        "co_ei": {"takeoff": 0.12, "climbout": 0.39, "approach": 2.45, "idle": 42.43, "lto_total_g": 23296},
        "nox_ei": {"takeoff": 50.35, "climbout": 34.92, "approach": 15.99, "idle": 5.12, "lto_total_g": 32941},
    },
    "GE90-115B__2": {
        "manufacturer": "General Electric Company",
        "bpr": 7.1,
        "opr": 42.2,
        "rated_thrust_kN": 513.9,
        "fuel_flow": {"takeoff": 4.690, "climbout": 3.670, "approach": 1.130, "idle": 0.380, "lto_cycle": 1546},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.03, "approach": 0.06, "idle": 4.24, "lto_total_g": 2559},
        "co_ei": {"takeoff": 0.08, "climbout": 0.07, "approach": 1.98, "idle": 39.11, "lto_total_g": 23858},
        "nox_ei": {"takeoff": 50.34, "climbout": 35.98, "approach": 16.50, "idle": 5.19, "lto_total_g": 34888},
    },
    "GE90-110B1": {
        "manufacturer": "General Electric Company",
        "bpr": 7.2,
        "opr": 40.6,
        "rated_thrust_kN": 492.7,
        "fuel_flow": {"takeoff": 4.221, "climbout": 3.370, "approach": 1.024, "idle": 0.332, "lto_cycle": 1386},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.04, "idle": 6.32, "lto_total_g": 3300},
        "co_ei": {"takeoff": 0.05, "climbout": 0.50, "approach": 2.94, "idle": 44.12, "lto_total_g": 23793},
        "nox_ei": {"takeoff": 44.93, "climbout": 32.57, "approach": 15.40, "idle": 5.02, "lto_total_g": 28841},
    },
    "GE90-110B1__2": {
        "manufacturer": "General Electric Company",
        "bpr": 7.3,
        "opr": 40.4,
        "rated_thrust_kN": 492.6,
        "fuel_flow": {"takeoff": 4.226, "climbout": 3.375, "approach": 1.029, "idle": 0.334, "lto_cycle": 1391},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.05, "idle": 3.87, "lto_total_g": 2043},
        "co_ei": {"takeoff": 0.13, "climbout": 0.14, "approach": 2.50, "idle": 35.72, "lto_total_g": 19317},
        "nox_ei": {"takeoff": 45.25, "climbout": 34.39, "approach": 15.53, "idle": 5.42, "lto_total_g": 30010},
    },
    "GE90-110B1__3": {
        "manufacturer": "General Electric Company",
        "bpr": 7.3,
        "opr": 39.7,
        "rated_thrust_kN": 492.6,
        "fuel_flow": {"takeoff": 4.320, "climbout": 3.470, "approach": 1.080, "idle": 0.370, "lto_cycle": 1479},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.06, "idle": 4.55, "lto_total_g": 2679},
        "co_ei": {"takeoff": 0.07, "climbout": 0.07, "approach": 2.29, "idle": 40.59, "lto_total_g": 24212},
        "nox_ei": {"takeoff": 44.44, "climbout": 33.85, "approach": 15.78, "idle": 5.11, "lto_total_g": 30616},
    },
    "Trent 970-84": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 7.5,
        "opr": 39.0,
        "rated_thrust_kN": 334.7,
        "fuel_flow": {"takeoff": 2.6, "climbout": 2.2, "approach": 0.7, "idle": 0.3, "lto_cycle": 980},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 0.2, "lto_total_g": 81},
        "co_ei": {"takeoff": 0.4, "climbout": 0.2, "approach": 1.4, "idle": 15.1, "lto_total_g": 6461},
        "nox_ei": {"takeoff": 37.2, "climbout": 29.1, "approach": 11.4, "idle": 5.1, "lto_total_g": 16555},
    },
    "Trent 972-84": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 7.5,
        "opr": 38.6,
        "rated_thrust_kN": 345.9,
        "fuel_flow": {"takeoff": 2.69, "climbout": 2.23, "approach": 0.75, "idle": 0.27, "lto_cycle": 1009},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 0.24, "lto_total_g": 101},
        "co_ei": {"takeoff": 0.4, "climbout": 0.3, "approach": 1.4, "idle": 15.94, "lto_total_g": 7099},
        "nox_ei": {"takeoff": 38.8, "climbout": 29.6, "approach": 11.8, "idle": 5.0, "lto_total_g": 17327},
    },
    "GEnx-2B67/P": {
        "manufacturer": "General Electric Company",
        "bpr": 8.0,
        "opr": 43.6,
        "rated_thrust_kN": 299.8,
        "fuel_flow": {"takeoff": 2.453, "climbout": 2.009, "approach": 0.642, "idle": 0.219, "lto_cycle": 864},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.02, "approach": 0.04, "idle": 0.41, "lto_total_g": 154},
        "co_ei": {"takeoff": 0.07, "climbout": 0.17, "approach": 1.78, "idle": 14.28, "lto_total_g": 5201},
        "nox_ei": {"takeoff": 34.21, "climbout": 21.1, "approach": 11.11, "idle": 4.92, "lto_total_g": 12509},
    },
    "Trent XWB-97": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 8.1,
        "opr": 48.4,
        "rated_thrust_kN": 436.7,
        "fuel_flow": {"takeoff": 3.498, "climbout": 2.798, "approach": 0.918, "idle": 0.301, "lto_cycle": 1206},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 0.01, "lto_total_g": 5},
        "co_ei": {"takeoff": 0.36, "climbout": 0.40, "approach": 0.82, "idle": 7.75, "lto_total_g": 4016},
        "nox_ei": {"takeoff": 66.05, "climbout": 48.51, "approach": 14.86, "idle": 5.64, "lto_total_g": 33540},
    },
    "LEAP-1B28BBJ1": {
        "manufacturer": "CFM International",
        "bpr": 8.2,
        "opr": 42.0,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.070, "climbout": 0.870, "approach": 0.290, "idle": 0.100, "lto_cycle": 386},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.02, "approach": 0.03, "idle": 0.38, "lto_total_g": 65},
        "co_ei": {"takeoff": 0.19, "climbout": 0.14, "approach": 1.09, "idle": 13.90, "lto_total_g": 2278},
        "nox_ei": {"takeoff": 72.75, "climbout": 30.75, "approach": 11.09, "idle": 4.93, "lto_total_g": 8343},
    },
    "LEAP-1B28BBJ2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.51, "lto_total_g": 85},
        "co_ei": {"takeoff": 0.17, "climbout": 0.14, "approach": 1.11, "idle": 14.4, "lto_total_g": 2221},
        "nox_ei": {"takeoff": 55.26, "climbout": 23.26, "approach": 11.59, "idle": 4.59, "lto_total_g": 6326},
    },
    "LEAP-1B27": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.51, "lto_total_g": 85},
        "co_ei": {"takeoff": 0.17, "climbout": 0.14, "approach": 1.11, "idle": 14.4, "lto_total_g": 2221},
        "nox_ei": {"takeoff": 55.26, "climbout": 23.26, "approach": 11.59, "idle": 4.59, "lto_total_g": 6326},
    },
    "LEAP-1B28B2C": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.51, "lto_total_g": 85},
        "co_ei": {"takeoff": 0.17, "climbout": 0.14, "approach": 1.11, "idle": 14.4, "lto_total_g": 2221},
        "nox_ei": {"takeoff": 55.26, "climbout": 23.26, "approach": 11.59, "idle": 4.59, "lto_total_g": 6326},
    },
    "LEAP-1B28BBJ1__2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 42.0,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.075, "climbout": 0.873, "approach": 0.285, "idle": 0.097, "lto_cycle": 380},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.46, "lto_total_g": 79},
        "co_ei": {"takeoff": 0.18, "climbout": 0.15, "approach": 0.99, "idle": 13.77, "lto_total_g": 2176},
        "nox_ei": {"takeoff": 64.36, "climbout": 29.59, "approach": 11.92, "idle": 4.68, "lto_total_g": 7837},
    },
    "LEAP-1B28/28B2/28B1/28B3": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 42.0,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.075, "climbout": 0.873, "approach": 0.285, "idle": 0.097, "lto_cycle": 380},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.46, "lto_total_g": 79},
        "co_ei": {"takeoff": 0.18, "climbout": 0.15, "approach": 0.99, "idle": 13.77, "lto_total_g": 2176},
        "nox_ei": {"takeoff": 64.36, "climbout": 29.59, "approach": 11.92, "idle": 4.68, "lto_total_g": 7837},
    },
    "LEAP-1B28BBJ2__2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.010, "climbout": 0.824, "approach": 0.278, "idle": 0.098, "lto_cycle": 371},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.03, "idle": 0.41, "lto_total_g": 68},
        "co_ei": {"takeoff": 0.18, "climbout": 0.13, "approach": 1.21, "idle": 14.45, "lto_total_g": 2315},
        "nox_ei": {"takeoff": 60.49, "climbout": 24.12, "approach": 10.70, "idle": 4.85, "lto_total_g": 6645},
    },
    "LEAP-1B28B2C__2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.010, "climbout": 0.824, "approach": 0.278, "idle": 0.098, "lto_cycle": 371},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.03, "idle": 0.41, "lto_total_g": 68},
        "co_ei": {"takeoff": 0.18, "climbout": 0.13, "approach": 1.21, "idle": 14.45, "lto_total_g": 2315},
        "nox_ei": {"takeoff": 60.49, "climbout": 24.12, "approach": 10.70, "idle": 4.85, "lto_total_g": 6645},
    },
    "LEAP-1B28": {
        "manufacturer": "CFM International",
        "bpr": 8.6,
        "opr": 41.5,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.061, "climbout": 0.864, "approach": 0.277, "idle": 0.098, "lto_cycle": 378},
        "hc_ei": {"takeoff": 0.05, "climbout": 0.04, "approach": 0.05, "idle": 0.57, "lto_total_g": 97},
        "co_ei": {"takeoff": 0.18, "climbout": 0.14, "approach": 1.20, "idle": 14.62, "lto_total_g": 2339},
        "nox_ei": {"takeoff": 60.67, "climbout": 29.58, "approach": 11.24, "idle": 4.64, "lto_total_g": 7534},
    },
    "LEAP-1B27__2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.010, "climbout": 0.824, "approach": 0.278, "idle": 0.098, "lto_cycle": 371},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.03, "idle": 0.41, "lto_total_g": 68},
        "co_ei": {"takeoff": 0.18, "climbout": 0.13, "approach": 1.21, "idle": 14.45, "lto_total_g": 2315},
        "nox_ei": {"takeoff": 60.49, "climbout": 24.12, "approach": 10.70, "idle": 4.85, "lto_total_g": 6645},
    },
    "PW1217G": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 8.3,
        "opr": 32.7,
        "rated_thrust_kN": 75.7,
        "fuel_flow": {"takeoff": 0.634, "climbout": 0.524, "approach": 0.184, "idle": 0.069, "lto_cycle": 248},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.02, "approach": 0.01, "idle": 0.01, "lto_total_g": 5},
        "co_ei": {"takeoff": 0.3, "climbout": 0.4, "approach": 2.5, "idle": 14.2, "lto_total_g": 1678},
        "nox_ei": {"takeoff": 25.3, "climbout": 18.6, "approach": 8.6, "idle": 5.1, "lto_total_g": 2891},
    },
    "LEAP-1B25": {
        "manufacturer": "CFM International",
        "bpr": 8.4,
        "opr": 39.1,
        "rated_thrust_kN": 119.2,
        "fuel_flow": {"takeoff": 0.952, "climbout": 0.780, "approach": 0.266, "idle": 0.096, "lto_cycle": 357},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.01, "approach": 0.03, "idle": 0.45, "lto_total_g": 72},
        "co_ei": {"takeoff": 0.17, "climbout": 0.14, "approach": 1.34, "idle": 15.01, "lto_total_g": 2354},
        "nox_ei": {"takeoff": 48.22, "climbout": 19.99, "approach": 10.35, "idle": 4.76, "lto_total_g": 5361},
    },
    "LEAP-1B25__2": {
        "manufacturer": "CFM International",
        "bpr": 8.4,
        "opr": 38.4,
        "rated_thrust_kN": 119.2,
        "fuel_flow": {"takeoff": 0.946, "climbout": 0.773, "approach": 0.255, "idle": 0.093, "lto_cycle": 348},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.04, "approach": 0.05, "idle": 0.74, "lto_total_g": 116},
        "co_ei": {"takeoff": 0.16, "climbout": 0.14, "approach": 1.54, "idle": 16.01, "lto_total_g": 2438},
        "nox_ei": {"takeoff": 43.67, "climbout": 20.68, "approach": 10.0, "idle": 4.94, "lto_total_g": 5174},
    },
    "LEAP-1B23": {
        "manufacturer": "CFM International",
        "bpr": 8.4,
        "opr": 38,
        "rated_thrust_kN": 115.2,
        "fuel_flow": {"takeoff": 0.913, "climbout": 0.750, "approach": 0.258, "idle": 0.094, "lto_cycle": 347},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.01, "approach": 0.03, "idle": 0.48, "lto_total_g": 76},
        "co_ei": {"takeoff": 0.15, "climbout": 0.15, "approach": 1.45, "idle": 15.43, "lto_total_g": 2385},
        "nox_ei": {"takeoff": 40.11, "climbout": 17.98, "approach": 10.10, "idle": 4.70, "lto_total_g": 4638},
    },
    "LEAP-1B21": {
        "manufacturer": "CFM International",
        "bpr": 8.5,
        "opr": 36.9,
        "rated_thrust_kN": 111.3,
        "fuel_flow": {"takeoff": 0.874, "climbout": 0.721, "approach": 0.250, "idle": 0.093, "lto_cycle": 337},
        "hc_ei": {"takeoff": 0.02, "climbout": 0.01, "approach": 0.03, "idle": 0.51, "lto_total_g": 78},
        "co_ei": {"takeoff": 0.14, "climbout": 0.18, "approach": 1.58, "idle": 15.85, "lto_total_g": 2414},
        "nox_ei": {"takeoff": 31.57, "climbout": 16.70, "approach": 9.85, "idle": 4.63, "lto_total_g": 4010},
    },
    "Trent 972-84__2": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 8.4,
        "opr": 38.7,
        "rated_thrust_kN": 345.9,
        "fuel_flow": {"takeoff": 2.672, "climbout": 2.21, "approach": 0.735, "idle": 0.258, "lto_cycle": 983},
        "hc_ei": {"takeoff": 0.01, "climbout": 0.11, "approach": 0.07, "idle": 0.04, "lto_total_g": 60},
        "co_ei": {"takeoff": 0.32, "climbout": 0.31, "approach": 1.1, "idle": 13.0, "lto_total_g": 5557},
        "nox_ei": {"takeoff": 39.78, "climbout": 30.36, "approach": 12.23, "idle": 5.51, "lto_total_g": 17699},
    },
    "Trent 972E-84": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 8.4,
        "opr": 38.7,
        "rated_thrust_kN": 345.9,
        "fuel_flow": {"takeoff": 2.672, "climbout": 2.21, "approach": 0.735, "idle": 0.258, "lto_cycle": 983},
        "hc_ei": {"takeoff": 0.01, "climbout": 0.11, "approach": 0.07, "idle": 0.04, "lto_total_g": 60},
        "co_ei": {"takeoff": 0.32, "climbout": 0.31, "approach": 1.1, "idle": 13.0, "lto_total_g": 5557},
        "nox_ei": {"takeoff": 39.78, "climbout": 30.36, "approach": 12.23, "idle": 5.51, "lto_total_g": 17699},
    },
    # ---------------------------------------------------------------------
    # NOTE:
    # The table supplied in chat is very large. Additional engines can be
    # appended below using the same schema and duplicate-key convention.
    # ---------------------------------------------------------------------

    # User-specific engine retained for compatibility
    "M45H-01": {
        "manufacturer": None,
        "bpr": None,
        "opr": None,
        "rated_thrust_kN": None,
        "fuel_flow": {"takeoff": 0.498, "climbout": 0.416, "approach": 0.146, "idle": 0.053, "lto_cycle": None},
        "hc_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "co_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "nox_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
    },
    "AS907-1-1A": {
        "manufacturer": None,
        "bpr": None,
        "opr": None,
        "rated_thrust_kN": None,
        "fuel_flow": {"takeoff": 0.347, "climbout": 0.288, "approach": 0.104, "idle": 0.048, "lto_cycle": None},
        "hc_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "co_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "nox_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
    },
    "JT3D-7": {
        "manufacturer": None,
        "bpr": None,
        "opr": None,
        "rated_thrust_kN": None,
        "fuel_flow": {"takeoff": 1.254, "climbout": 1.032, "approach": 0.389, "idle": 0.128, "lto_cycle": None},
        "hc_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "co_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
        "nox_ei": {"takeoff": None, "climbout": None, "approach": None, "idle": None, "lto_total_g": None},
    },
}


# -----------------------------------------------------------------------------
# Diameter data (meters)
# -----------------------------------------------------------------------------
INCH_TO_M = 0.0254


def inches(value):
    return value * INCH_TO_M


engine_diameter_m = {
    # User-provided / already used engines
    "M45H-01": 0.909,

    # Pratt & Whitney / PW4000 family
    "PW4062": inches(94.0),
    "PW4x62": inches(94.0),

    # GE90
    "GE90-115B": inches(128.0),
    "GE90-115B__2": inches(128.0),
    "GE90-110B1": inches(128.0),
    "GE90-110B1__2": inches(128.0),
    "GE90-110B1__3": inches(128.0),

    # Trent family (family-level placeholders if exact variant not separately published)
    "Trent 970-84": 2.95,
    "Trent 970-84__2": 2.95,
    "Trent 972-84": 2.95,
    "Trent 972-84__2": 2.95,
    "Trent 972E-84": 2.95,
    "Trent XWB-97": 3.00,
    "Trent XWB-84EP": 3.00,
    "Trent XWB-79BEP": 3.00,
    "Trent XWB-79EP": 3.00,
    "Trent XWB-84": 3.00,
    "Trent XWB-84__2": 3.00,
    "Trent XWB-75EP": 3.00,
    "Trent XWB-79": 3.00,
    "Trent XWB-79__2": 3.00,
    "Trent XWB-79B": 3.00,
    "Trent XWB-79B__2": 3.00,
    "Trent XWB-75": 3.00,
    "Trent XWB-75__2": 3.00,
    "Trent 1000-J3": 2.85,
    "Trent 1000-J3__2": 2.85,
    "Trent 1000-K3": 2.85,
    "Trent 1000-K3__2": 2.85,
    "Trent 1000-M3": 2.85,
    "Trent 1000-N3": 2.85,
    "Trent 1000-Q3": 2.85,
    "Trent 1000-Q3__2": 2.85,
    "Trent 1000-R3": 2.85,
    "Trent 1000-CE3": 2.85,
    "Trent 1000-CE3__2": 2.85,
    "Trent 1000-D3": 2.85,
    "Trent 1000-D3__2": 2.85,
    "Trent 1000-L3": 2.85,
    "Trent 1000-L3__2": 2.85,
    "Trent 1000-P3": 2.85,
    "Trent 1000-P3__2": 2.85,
    "Trent 1000-G3": 2.85,
    "Trent 1000-G3__2": 2.85,
    "Trent 1000-AE3": 2.85,
    "Trent 1000-AE3__2": 2.85,
    "Trent 1000-H3": 2.85,
    "Trent 1000-H3__2": 2.85,
    "Trent7000-72": 2.84,
    "Trent7000-72C": 2.84,
    "Trent7000-72D": 2.84,
    "Trent7000-70": 2.84,
    "Trent7000-68": 2.84,

    # CFM56 families
    "CFM56-5B1/3": 1.735,
    "CFM56-5B2/3": 1.735,
    "CFM56-5B3/3": 1.735,
    "CFM56-5B4/3": 1.735,
    "CFM56-5B5/3": 1.735,
    "CFM56-5B6/3": 1.735,
    "CFM56-5B7/3": 1.735,
    "CFM56-5B8/3": 1.735,
    "CFM56-5B9/3": 1.735,
    "CFM56-7B20E": 1.55,
    "CFM56-7B22E": 1.55,
    "CFM56-7B22E/B1": 1.55,
    "CFM56-7B24E": 1.55,
    "CFM56-7B26E": 1.55,
    "CFM56-7B27AE": 1.55,

    # CF34 families
    "CF34-3B": 1.245,
    "CF34-8C5": 1.32,
    "CF34-8C5A1": 1.32,
    "CF34-8C5A2": 1.32,
    "CF34-8C5A3": 1.32,
    "CF34-8C5B1": 1.32,
    "CF34-8E5": 1.36,
    "CF34-8E5__2": 1.36,
    "CF34-8E5A1": 1.36,
    "CF34-8E5A2HA": 1.36,
    "CF34-10A16/B/C/D": 1.52,
    "CF34-10A16": 1.52,
    "CF34-10A16/16-B": 1.52,

    # CF6 families
    "CF6-80C2B5F/B6F/B7F": 2.36,
    "CF6-80C2B5F": 2.36,
    "CF6-80C2B1F": 2.36,
    "CF6-80C2B1F__2": 2.36,
    "CF6-80C2B6F": 2.36,

    # GEnx families
    "GEnx-2B67/P": 2.67,
    "GEnx-1B76/P2": 2.82,
    "GEnx-1B76A/P2": 2.82,
    "GEnx-1B75/P2": 2.82,
    "GEnx-1B74/75/P2": 2.82,
    "GEnx-1B76A/P2, 1B76/P2": 2.82,
    "GEnx-1B75/P2__2": 2.82,
    "GEnx-1B74/75/P2__2": 2.82,
    "GEnx-1B70/72/P2": 2.82,
    "GEnx-1B70/75/P2": 2.82,
    "GEnx-1B70/P2": 2.82,
    "GEnx-1B70/75/P2, 1B70/72/P2, 1B70C/P2, 1B70/P2": 2.82,
    "GEnx-1B67/P2": 2.82,
    "GEnx-1B67/P2__2": 2.82,
    "GEnx-1B64/P2": 2.82,
    "GEnx-1B64/P2__2": 2.82,
    "GEnx-1B58/P2": 2.82,
    "GEnx-1B58/P2__2": 2.82,
    "GEnx-1B54/P2": 2.82,
    "GEnx-1B54/P2__2": 2.82,

    # LEAP families
    "LEAP-1B21": 1.75,
    "LEAP-1B23": 1.75,
    "LEAP-1B25": 1.75,
    "LEAP-1B25__2": 1.75,
    "LEAP-1B25__3": 1.75,
    "LEAP-1B27": 1.75,
    "LEAP-1B27__2": 1.75,
    "LEAP-1B28": 1.75,
    "LEAP-1B28B2": 1.75,
    "LEAP-1B28B2C": 1.75,
    "LEAP-1B28B2C__2": 1.75,
    "LEAP-1B28BBJ1": 1.75,
    "LEAP-1B28BBJ1__2": 1.75,
    "LEAP-1B28BBJ2": 1.75,
    "LEAP-1B28BBJ2__2": 1.75,
    "LEAP-1B28/28B1/28B2/28B3": 1.75,
    "LEAP-1B28/28B2/28B1/28B3": 1.75,
    "LEAP-1A35A/35AX/33/33X/33B2/33B2X/32/32X/30": 1.98,
    "LEAP-1A35A/33/33B2/32/30": 1.98,
    "LEAP-1A35A/33/33B2/32/30__2": 1.98,
    "LEAP-1A29CJ": 1.98,
    "LEAP-1A29": 1.98,
    "LEAP-1A29__2": 1.98,
    "LEAP-1A29CJ__2": 1.98,
    "LEAP-1A26CJ": 1.98,
    "LEAP-1A26/26E1": 1.98,
    "LEAP-1A26/26E1__2": 1.98,
    "LEAP-1A26CJ__2": 1.98,
    "LEAP-1A24/24E1/23": 1.98,
    "LEAP-1A24/24E1/23__2": 1.98,
    "LEAP-1C30/30B1": 1.98,
    "LEAP-1C28": 1.98,

    # Pratt geared turbofan families
    "PW1217G": 1.42,
    "PW1215G": 1.42,
    "PW1525G": 1.42,
    "PW1524G": 1.42,
    "PW1521G": 1.42,
    "PW1521GA": 1.42,
    "PW1922G": 1.42,
    "PW1923G-A": 1.42,
    "PW1923G": 1.42,
    "PW1921G": 1.42,
    "PW1919G": 1.42,
    "PW1519G": 1.42,
    "PW1130G-JM": 2.06,
    "PW1133GA-JM": 2.06,
    "PW1133G-JM": 2.06,
    "PW1431GH-JM": 2.06,
    "PW1129G-JM": 2.06,
    "PW1428GH-JM": 2.06,
    "PW1127G1-JM": 2.06,
    "PW1122G-JM": 2.06,

    # Other Pratt engines
    "PW307A": 1.04,
    "PW815GA": 1.45,
    "PW814GA": 1.45,

    # Other engines from user's list
    "AS907-1-1A": 1.27,
    "JT3D-7": 1.32,
    "D-36 ser. 4A": 1.42,
    "D-436-148 F1": 1.4,
    "D-436-148 F2": 1.4,
}


engine_diameter_aliases = {
    "TRENT970-84": "Trent 970-84",
    "TRENT972-84": "Trent 972-84",
    "TRENT972E-84": "Trent 972E-84",
}


def canonical_engine_name(engine_name):
    return engine_diameter_aliases.get(engine_name, engine_name)


def get_engine_diameter(engine_name, default=None):
    """Return engine/fan diameter in meters for a given engine key."""
    key = canonical_engine_name(engine_name)
    return engine_diameter_m.get(key, default)


# -----------------------------------------------------------------------------
# Helper views from master dictionary
# -----------------------------------------------------------------------------
def build_reference_dict(master_data, section):
    ref = {}
    for eng, values in master_data.items():
        if section in values and values[section] is not None:
            ref[eng] = dict(values[section])
    return ref


ICAO_fuel_flow = build_reference_dict(icao_data, "fuel_flow")
ICAO_hc_ei = build_reference_dict(icao_data, "hc_ei")
ICAO_co_ei = build_reference_dict(icao_data, "co_ei")
ICAO_nox_ei = build_reference_dict(icao_data, "nox_ei")


# -----------------------------------------------------------------------------
# Engine-definition helpers
# -----------------------------------------------------------------------------
def build_define_engine_kwargs(engine_name, fbpr=None, use_opr_as_cpr=True, include_diameter=True):
    """Build kwargs commonly needed for define_engine(...) from ICAO data.

    Parameters
    ----------
    engine_name : str
        Key present in icao_data.
    fbpr : float | None
        Fan bypass ratio or user placeholder if define_engine needs it.
    use_opr_as_cpr : bool
        If True, uses ICAO overall pressure ratio as CPR.
    include_diameter : bool
        If True, include D when available.
    """
    key = canonical_engine_name(engine_name)
    if key not in icao_data:
        raise KeyError(f"Engine {engine_name!r} not found in icao_data")

    row = icao_data[key]
    kwargs = {
        "BPR": row.get("bpr"),
        "design_thrust": None if row.get("rated_thrust_kN") is None else row["rated_thrust_kN"] * 1000.0,
    }

    if use_opr_as_cpr:
        kwargs["CPR"] = row.get("opr")
    if fbpr is not None:
        kwargs["FBPR"] = fbpr
    if include_diameter:
        dval = get_engine_diameter(key)
        if dval is not None:
            kwargs["D"] = dval

    return kwargs


def filter_none_values(mapping):
    """Return a copy of mapping without keys whose value is None."""
    return {k: v for k, v in mapping.items() if v is not None}


def make_engine_definition(engine_name, define_engine_func, fbpr=None, use_opr_as_cpr=True, include_diameter=True, extra_kwargs=None):
    """Create an engine object by calling user-supplied define_engine(...)."""
    kwargs = build_define_engine_kwargs(
        engine_name,
        fbpr=fbpr,
        use_opr_as_cpr=use_opr_as_cpr,
        include_diameter=include_diameter,
    )
    kwargs = filter_none_values(kwargs)
    if extra_kwargs:
        kwargs.update(extra_kwargs)
    return define_engine_func(**kwargs)


def attach_diameter(engine_dict):
    """Return a copy of an engine settings dict with D added where available.

    This is only useful if each entry looks like:
        {"engine": { ... kwargs dict ... }, ...}
    rather than already containing a built engine object.
    """
    out = {}
    for name, cfg in engine_dict.items():
        cfg2 = deepcopy(cfg)
        if isinstance(cfg2.get("engine"), dict) and "D" not in cfg2["engine"]:
            dval = get_engine_diameter(name)
            if dval is not None:
                cfg2["engine"]["D"] = dval
        out[name] = cfg2
    return out


# -----------------------------------------------------------------------------
# Comparison helpers aligned with user's workflow
# -----------------------------------------------------------------------------
def compare_lto_reference(LTO_results, operating_points, reference_dict, result_key, total_label="TOTAL"):
    """Compare modeled LTO point results against a reference dictionary.

    Parameters
    ----------
    LTO_results : dict
        Example: LTO_results[name][point_name][result_key]
    operating_points : dict
        Example: operating_points[point_name]["time"]
    reference_dict : dict
        Example: ICAO_fuel_flow or ICAO_nox_ei
    result_key : str
        Example: "fuel_mass_flow"
    total_label : str
        Label used for total row.

    Returns
    -------
    dict
        Nested dict of percentage differences by engine and operating point.
    """
    output = {}

    for name, results in LTO_results.items():
        output[name] = {}

        ref_name = canonical_engine_name(name)
        if ref_name not in reference_dict:
            continue

        total_model = 0.0
        total_ref = 0.0

        for point_name, point in operating_points.items():
            duration = point["time"]
            model_value = results[point_name][result_key]
            ref_value = reference_dict[ref_name][point_name]

            model_mass = model_value * duration
            ref_mass = ref_value * duration

            if ref_mass == 0:
                percent_difference = None
            else:
                percent_difference = (model_mass - ref_mass) / ref_mass * 100.0

            output[name][point_name] = percent_difference
            total_model += model_mass
            total_ref += ref_mass

        if total_ref == 0:
            output[name][total_label] = None
        else:
            output[name][total_label] = (total_model - total_ref) / total_ref * 100.0

    return output


def build_fuel_burn_percent_difference(LTO_results, operating_points):
    """Convenience wrapper for fuel-flow comparison using ICAO_fuel_flow."""
    return compare_lto_reference(
        LTO_results=LTO_results,
        operating_points=operating_points,
        reference_dict=ICAO_fuel_flow,
        result_key="fuel_mass_flow",
    )


def format_percent(value):
    if value is None:
        return "None"
    return f"{value:+.2f}%"
