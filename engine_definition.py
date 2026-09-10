"""Ready-to-paste engine definitions and usage helpers.

This file gives you:
1. define_all_engines(define_engine): returns a dictionary of engine objects
   keyed by ICAO engine name.
2. build_engines_config(engine_objects, default_conditions=None, t04_map=None):
   builds your main `engines = {...}` structure.
3. ICAO_fuel_flow extracted in the same shape as your original workflow.
4. compute_lto_fuel_burn_percent_difference(...): same calculation pattern you
   were already using, but extended to all engines.

Notes:
- FPR and FBPR are engineering defaults/estimates, not ICAO-certified values.
- Diameter values are family/public-reference values where available, otherwise
  reasonable placeholders so your code can run.
- Duplicate ICAO rows with same engine name but different BPR/OPR/thrust are
  kept as suffixed keys like NAME__2.
"""

from copy import deepcopy
import pandas as pd


# -----------------------------------------------------------------------------
# Master ICAO-like data used to generate engine definitions
# -----------------------------------------------------------------------------
icao_data = {
    "PW307A": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 4.2,
        "opr": 20.2,
        "rated_thrust_kN": 28.5,
        "fuel_flow": {"takeoff": 0.329, "climbout": 0.274, "approach": 0.102, "idle": 0.045, "lto_cycle": 144},
    },
    "PW4062": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 4.6,
        "opr": 31.0,
        "rated_thrust_kN": 275.8,
        "fuel_flow": {"takeoff": 2.725, "climbout": 2.125, "approach": 0.718, "idle": 0.210, "lto_cycle": 894},
    },
    "PW4x62": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 4.6,
        "opr": 31.9,
        "rated_thrust_kN": 275.8,
        "fuel_flow": {"takeoff": 2.767, "climbout": 2.166, "approach": 0.708, "idle": 0.223, "lto_cycle": 920},
    },
    "CF34-8E5A2HA": {
        "manufacturer": "General Electric Company",
        "bpr": 4.7,
        "opr": 25.4,
        "rated_thrust_kN": 64.5,
        "fuel_flow": {"takeoff": 0.721, "climbout": 0.588, "approach": 0.196, "idle": 0.067, "lto_cycle": 260},
    },
    "CF34-8E5A1": {
        "manufacturer": "General Electric Company",
        "bpr": 4.7,
        "opr": 24.7,
        "rated_thrust_kN": 62.5,
        "fuel_flow": {"takeoff": 0.691, "climbout": 0.565, "approach": 0.190, "idle": 0.066, "lto_cycle": 252},
    },
    "CF34-8E5": {
        "manufacturer": "General Electric Company",
        "bpr": 4.7,
        "opr": 23.8,
        "rated_thrust_kN": 59.7,
        "fuel_flow": {"takeoff": 0.652, "climbout": 0.536, "approach": 0.182, "idle": 0.065, "lto_cycle": 243},
    },
    "D-436-148 F1": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 4.9,
        "opr": 19.8,
        "rated_thrust_kN": 64.4,
        "fuel_flow": {"takeoff": 0.548, "climbout": 0.468, "approach": 0.218, "idle": 0.093, "lto_cycle": 260},
    },
    "D-436-148 F2": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 4.9,
        "opr": 20.7,
        "rated_thrust_kN": 68.7,
        "fuel_flow": {"takeoff": 0.581, "climbout": 0.493, "approach": 0.225, "idle": 0.099, "lto_cycle": 274},
    },
    "CF6-80C2B5F/B6F/B7F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.0,
        "opr": 32.7,
        "rated_thrust_kN": 267.0,
        "fuel_flow": {"takeoff": 2.569, "climbout": 2.074, "approach": 0.671, "idle": 0.196, "lto_cycle": 848},
    },
    "D-36 ser. 4A": {
        "manufacturer": "IVCHENKO PROGRESS ZMBK",
        "bpr": 5.0,
        "opr": 19.9,
        "rated_thrust_kN": 63.8,
        "fuel_flow": {"takeoff": 0.634, "climbout": 0.533, "approach": 0.211, "idle": 0.092, "lto_cycle": 265},
    },
    "CFM56-7B26E": {
        "manufacturer": "CFM International",
        "bpr": 5.1,
        "opr": 27.7,
        "rated_thrust_kN": 117.0,
        "fuel_flow": {"takeoff": 1.213, "climbout": 0.986, "approach": 0.331, "idle": 0.108, "lto_cycle": 429},
    },
    "CFM56-7B27AE": {
        "manufacturer": "CFM International",
        "bpr": 5.1,
        "opr": 29.0,
        "rated_thrust_kN": 121.4,
        "fuel_flow": {"takeoff": 1.293, "climbout": 1.031, "approach": 0.343, "idle": 0.110, "lto_cycle": 444},
    },
    "CF6-80C2B5F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 32.8,
        "rated_thrust_kN": 272.5,
        "fuel_flow": {"takeoff": 2.685, "climbout": 2.162, "approach": 0.697, "idle": 0.206, "lto_cycle": 887},
    },
    "CF6-80C2B1F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 30.1,
        "rated_thrust_kN": 254.3,
        "fuel_flow": {"takeoff": 2.422, "climbout": 1.983, "approach": 0.650, "idle": 0.199, "lto_cycle": 830},
    },
    "CF6-80C2B6F": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 31.7,
        "rated_thrust_kN": 267.0,
        "fuel_flow": {"takeoff": 2.594, "climbout": 2.104, "approach": 0.682, "idle": 0.203, "lto_cycle": 867},
    },
    "CF34-8C5": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.1,
        "rated_thrust_kN": 59.4,
        "fuel_flow": {"takeoff": 0.648, "climbout": 0.530, "approach": 0.179, "idle": 0.064, "lto_cycle": 240},
    },
    "CF34-8C5A1": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.5,
        "rated_thrust_kN": 60.6,
        "fuel_flow": {"takeoff": 0.665, "climbout": 0.543, "approach": 0.183, "idle": 0.065, "lto_cycle": 245},
    },
    "CF34-8C5A2": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 24.1,
        "rated_thrust_kN": 62.5,
        "fuel_flow": {"takeoff": 0.691, "climbout": 0.563, "approach": 0.188, "idle": 0.066, "lto_cycle": 251},
    },
    "CF34-8C5A3": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 24.8,
        "rated_thrust_kN": 64.5,
        "fuel_flow": {"takeoff": 0.721, "climbout": 0.586, "approach": 0.193, "idle": 0.067, "lto_cycle": 259},
    },
    "CF34-8C5B1": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 22.1,
        "rated_thrust_kN": 56.4,
        "fuel_flow": {"takeoff": 0.606, "climbout": 0.497, "approach": 0.171, "idle": 0.063, "lto_cycle": 230},
    },
    "CF34-8E5__2": {
        "manufacturer": "General Electric Company",
        "bpr": 5.1,
        "opr": 23.2,
        "rated_thrust_kN": 59.7,
        "fuel_flow": {"takeoff": 0.652, "climbout": 0.533, "approach": 0.180, "idle": 0.064, "lto_cycle": 241},
    },
    "CFM56-7B22E": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 24.2,
        "rated_thrust_kN": 101.0,
        "fuel_flow": {"takeoff": 1.004, "climbout": 0.832, "approach": 0.291, "idle": 0.099, "lto_cycle": 376},
    },
    "CFM56-7B22E/B1": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 24.2,
        "rated_thrust_kN": 101.0,
        "fuel_flow": {"takeoff": 1.004, "climbout": 0.832, "approach": 0.291, "idle": 0.099, "lto_cycle": 376},
    },
    "CFM56-7B24E": {
        "manufacturer": "CFM International",
        "bpr": 5.3,
        "opr": 25.6,
        "rated_thrust_kN": 107.6,
        "fuel_flow": {"takeoff": 1.086, "climbout": 0.895, "approach": 0.308, "idle": 0.103, "lto_cycle": 398},
    },
    "CFM56-5B3/3": {
        "manufacturer": "CFM International",
        "bpr": 5.4,
        "opr": 32.6,
        "rated_thrust_kN": 142.3,
        "fuel_flow": {"takeoff": 1.462, "climbout": 1.153, "approach": 0.369, "idle": 0.113, "lto_cycle": 478},
    },
    "CFM56-5B1/3": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 30.2,
        "rated_thrust_kN": 133.4,
        "fuel_flow": {"takeoff": 1.318, "climbout": 1.063, "approach": 0.347, "idle": 0.109, "lto_cycle": 448},
    },
    "CFM56-5B2/3": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 31.3,
        "rated_thrust_kN": 137.9,
        "fuel_flow": {"takeoff": 1.385, "climbout": 1.107, "approach": 0.358, "idle": 0.111, "lto_cycle": 463},
    },
    "CFM56-7B20E": {
        "manufacturer": "CFM International",
        "bpr": 5.5,
        "opr": 22.4,
        "rated_thrust_kN": 91.6,
        "fuel_flow": {"takeoff": 0.896, "climbout": 0.746, "approach": 0.268, "idle": 0.094, "lto_cycle": 348},
    },
    "CF34-10A16/B/C/D": {
        "manufacturer": "General Electric Company",
        "bpr": 5.6,
        "opr": 24.8,
        "rated_thrust_kN": 77.0,
        "fuel_flow": {"takeoff": 0.771, "climbout": 0.638, "approach": 0.216, "idle": 0.085, "lto_cycle": 302},
    },
    "PW815GA": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 5.6,
        "opr": 35.0,
        "rated_thrust_kN": 71.2,
        "fuel_flow": {"takeoff": 0.699, "climbout": 0.573, "approach": 0.201, "idle": 0.071, "lto_cycle": 264},
    },
    "PW814GA": {
        "manufacturer": "Pratt & Whitney Canada",
        "bpr": 5.7,
        "opr": 33.9,
        "rated_thrust_kN": 68.6,
        "fuel_flow": {"takeoff": 0.667, "climbout": 0.549, "approach": 0.194, "idle": 0.070, "lto_cycle": 256},
    },
    "CFM56-5B4/3": {
        "manufacturer": "CFM International",
        "bpr": 5.7,
        "opr": 27.3,
        "rated_thrust_kN": 120.1,
        "fuel_flow": {"takeoff": 1.142, "climbout": 0.939, "approach": 0.316, "idle": 0.102, "lto_cycle": 407},
    },
    "CFM56-5B7/3": {
        "manufacturer": "CFM International",
        "bpr": 5.7,
        "opr": 27.3,
        "rated_thrust_kN": 120.1,
        "fuel_flow": {"takeoff": 1.142, "climbout": 0.939, "approach": 0.316, "idle": 0.102, "lto_cycle": 407},
    },
    "CF34-10A16": {
        "manufacturer": "General Electric Company",
        "bpr": 5.7,
        "opr": 25.1,
        "rated_thrust_kN": 76.9,
        "fuel_flow": {"takeoff": 0.765, "climbout": 0.632, "approach": 0.219, "idle": 0.083, "lto_cycle": 298},
    },
    "CF34-10A16/16-B": {
        "manufacturer": "General Electric Company",
        "bpr": 5.7,
        "opr": 25.1,
        "rated_thrust_kN": 76.9,
        "fuel_flow": {"takeoff": 0.765, "climbout": 0.632, "approach": 0.219, "idle": 0.083, "lto_cycle": 298},
    },
    "CFM56-5B6/3": {
        "manufacturer": "CFM International",
        "bpr": 5.9,
        "opr": 24.3,
        "rated_thrust_kN": 104.5,
        "fuel_flow": {"takeoff": 0.965, "climbout": 0.800, "approach": 0.279, "idle": 0.095, "lto_cycle": 361},
    },
    "CFM56-5B9/3": {
        "manufacturer": "CFM International",
        "bpr": 5.9,
        "opr": 24.2,
        "rated_thrust_kN": 103.6,
        "fuel_flow": {"takeoff": 0.956, "climbout": 0.793, "approach": 0.278, "idle": 0.095, "lto_cycle": 359},
    },
    "CFM56-5B5/3": {
        "manufacturer": "CFM International",
        "bpr": 6.0,
        "opr": 23.1,
        "rated_thrust_kN": 97.9,
        "fuel_flow": {"takeoff": 0.894, "climbout": 0.743, "approach": 0.264, "idle": 0.092, "lto_cycle": 343},
    },
    "CFM56-5B8/3": {
        "manufacturer": "CFM International",
        "bpr": 6.0,
        "opr": 22.7,
        "rated_thrust_kN": 96.1,
        "fuel_flow": {"takeoff": 0.875, "climbout": 0.727, "approach": 0.260, "idle": 0.091, "lto_cycle": 338},
    },
    "CF34-3B": {
        "manufacturer": "General Electric Company",
        "bpr": 6.3,
        "opr": 19.3,
        "rated_thrust_kN": 41.0,
        "fuel_flow": {"takeoff": 0.399, "climbout": 0.329, "approach": 0.116, "idle": 0.049, "lto_cycle": 164},
    },
    "GE90-115B": {
        "manufacturer": "General Electric Company",
        "bpr": 7.1,
        "opr": 42.2,
        "rated_thrust_kN": 513.9,
        "fuel_flow": {"takeoff": 4.690, "climbout": 3.670, "approach": 1.130, "idle": 0.380, "lto_cycle": 1546},
    },
    "GE90-110B1": {
        "manufacturer": "General Electric Company",
        "bpr": 7.3,
        "opr": 39.7,
        "rated_thrust_kN": 492.6,
        "fuel_flow": {"takeoff": 4.320, "climbout": 3.470, "approach": 1.080, "idle": 0.370, "lto_cycle": 1479},
    },
    "GEnx-2B67/P": {
        "manufacturer": "General Electric Company",
        "bpr": 8.0,
        "opr": 43.6,
        "rated_thrust_kN": 299.8,
        "fuel_flow": {"takeoff": 2.453, "climbout": 2.009, "approach": 0.642, "idle": 0.219, "lto_cycle": 864},
    },
    "Trent XWB-97": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 8.1,
        "opr": 48.4,
        "rated_thrust_kN": 436.7,
        "fuel_flow": {"takeoff": 3.498, "climbout": 2.798, "approach": 0.918, "idle": 0.301, "lto_cycle": 1206},
    },
    "LEAP-1B28BBJ1": {
        "manufacturer": "CFM International",
        "bpr": 8.2,
        "opr": 42.0,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.070, "climbout": 0.870, "approach": 0.290, "idle": 0.100, "lto_cycle": 386},
    },
    "LEAP-1B28BBJ2": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
    },
    "LEAP-1B27": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
    },
    "LEAP-1B28B2C": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 40.5,
        "rated_thrust_kN": 124.7,
        "fuel_flow": {"takeoff": 1.014, "climbout": 0.826, "approach": 0.273, "idle": 0.095, "lto_cycle": 365},
    },
    "LEAP-1B28/28B2/28B1/28B3": {
        "manufacturer": "CFM International",
        "bpr": 8.3,
        "opr": 42.0,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.075, "climbout": 0.873, "approach": 0.285, "idle": 0.097, "lto_cycle": 380},
    },
    "PW1217G": {
        "manufacturer": "Pratt & Whitney",
        "bpr": 8.3,
        "opr": 32.7,
        "rated_thrust_kN": 75.7,
        "fuel_flow": {"takeoff": 0.634, "climbout": 0.524, "approach": 0.184, "idle": 0.069, "lto_cycle": 248},
    },
    "LEAP-1B25": {
        "manufacturer": "CFM International",
        "bpr": 8.4,
        "opr": 39.1,
        "rated_thrust_kN": 119.2,
        "fuel_flow": {"takeoff": 0.952, "climbout": 0.780, "approach": 0.266, "idle": 0.096, "lto_cycle": 357},
    },
    "LEAP-1B23": {
        "manufacturer": "CFM International",
        "bpr": 8.4,
        "opr": 38.0,
        "rated_thrust_kN": 115.2,
        "fuel_flow": {"takeoff": 0.913, "climbout": 0.750, "approach": 0.258, "idle": 0.094, "lto_cycle": 347},
    },
    "LEAP-1B21": {
        "manufacturer": "CFM International",
        "bpr": 8.5,
        "opr": 36.9,
        "rated_thrust_kN": 111.3,
        "fuel_flow": {"takeoff": 0.874, "climbout": 0.721, "approach": 0.250, "idle": 0.093, "lto_cycle": 337},
    },
    "LEAP-1B28": {
        "manufacturer": "CFM International",
        "bpr": 8.6,
        "opr": 41.5,
        "rated_thrust_kN": 130.4,
        "fuel_flow": {"takeoff": 1.061, "climbout": 0.864, "approach": 0.277, "idle": 0.098, "lto_cycle": 378},
    },
}


# -----------------------------------------------------------------------------
# Diameter defaults / estimates [m]
# -----------------------------------------------------------------------------
engine_diameter_m = {
    "PW307A": 1.0414,
    "PW4062": 2.3876,
    "PW4x62": 2.3876,
    "CF34-8E5A2HA": 1.295,
    "CF34-8E5A1": 1.295,
    "CF34-8E5": 1.295,
    "D-436-148 F1": 1.37,
    "D-436-148 F2": 1.37,
    "CF6-80C2B5F/B6F/B7F": 2.36,
    "D-36 ser. 4A": 1.49,
    "CFM56-7B26E": 1.55,
    "CFM56-7B27AE": 1.55,
    "CF6-80C2B5F": 2.36,
    "CF6-80C2B1F": 2.36,
    "CF6-80C2B6F": 2.36,
    "CF6-80C2B1F__2": 2.36,
    "CF34-8C5": 1.27,
    "CF34-8C5A1": 1.27,
    "CF34-8C5A2": 1.27,
    "CF34-8C5A3": 1.27,
    "CF34-8C5B1": 1.27,
    "CF34-8E5__2": 1.295,
    "CFM56-7B22E": 1.55,
    "CFM56-7B22E/B1": 1.55,
    "CFM56-7B24E": 1.55,
    "CFM56-7B24E/B1": 1.55,
    "CFM56-5B3/3": 1.735,
    "CFM56-5B1/3": 1.735,
    "CFM56-5B2/3": 1.735,
    "CFM56-7B20E": 1.55,
    "CF34-10A16/B/C/D": 1.346,
    "PW815GA": 1.42,
    "PW814GA": 1.42,
    "CFM56-5B4/3": 1.735,
    "CFM56-5B7/3": 1.735,
    "CF34-10A16": 1.346,
    "CF34-10A16/16-B": 1.346,
    "CFM56-5B6/3": 1.735,
    "CFM56-5B9/3": 1.735,
    "CFM56-5B5/3": 1.735,
    "CFM56-5B8/3": 1.735,
    "CF34-3B": 1.219,
    "GE90-115B": 3.2512,
    "GE90-110B1": 3.2512,
    "GEnx-2B67/P": 2.54,
    "Trent XWB-97": 3.00,
    "LEAP-1B28BBJ1": 1.753,
    "LEAP-1B28/28B1/28B2/28B3": 1.753,
    "LEAP-1B28BBJ2": 1.753,
    "LEAP-1B27": 1.753,
    "LEAP-1B28B2C": 1.753,
    "LEAP-1B28BBJ1__2": 1.753,
    "LEAP-1B28/28B2/28B1/28B3": 1.753,
    "PW1217G": 1.42,
    "LEAP-1B25": 1.753,
    "LEAP-1B23": 1.753,
    "LEAP-1B21": 1.753,
    "GEnx-1B76/P2": 2.819,
    "LEAP-1B28": 1.753,
    "LEAP-1B28B2": 1.753,
}


# -----------------------------------------------------------------------------
# FPR / FBPR defaults / estimates
# -----------------------------------------------------------------------------
engine_cycle_defaults = {
    "PW307A": {"FPR": 1.358, "FBPR": 2.00},
    "PW4062": {"FPR": 1.5, "FBPR": 2.5},
    "PW4x62": {"FPR": 1.5, "FBPR": 2.5},
    "PW815GA": {"FPR": 1.55, "FBPR": 2.60},
    "PW814GA": {"FPR": 1.55, "FBPR": 2.60},
    "D-436-148 F1": {"FPR": 1.5, "FBPR": 2.5},
    "D-436-148 F2": {"FPR": 1.5, "FBPR": 2.5},
    "D-36 ser. 4A": {"FPR": 1.5, "FBPR": 2.5},
    "CF6-80C2BF": {"FPR": 1.55, "FBPR": 2.60},
    "CF6-80C2B1F": {"FPR": 1.55, "FBPR": 2.60},
    "CF6-80C2B6F": {"FPR": 1.55, "FBPR": 2.60},
    "CF6-80C2B5F/B6F/B7F": {"FPR": 1.55, "FBPR": 2.60},
    "CF6-80C2B5F": {"FPR": 1.55, "FBPR": 2.60},
    "CFM56-5B1/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B2/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B3/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B4/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B5/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B6/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B7/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B8/3": {"FPR": 1.50, "FBPR": 2.0},
    "CFM56-5B9/3": {"FPR": 1.55, "FBPR": 2.48},
    "CFM56-7B20E": {"FPR": 1.55, "FBPR": 2.45},
    "CFM56-7B22E": {"FPR": 1.56, "FBPR": 2.48},
    "CFM56-7B22E/B1": {"FPR": 1.56, "FBPR": 2.48},
    "CFM56-7B24E": {"FPR": 1.58, "FBPR": 2.52},
    "CFM56-7B24E/B1": {"FPR": 1.58, "FBPR": 2.52},
    "CFM56-7B26E": {"FPR": 1.60, "FBPR": 2.55},
    "CFM56-7B27AE": {"FPR": 1.61, "FBPR": 2.58},
    "GE90-110B1": {"FPR": 1.60, "FBPR": 2.80},
    "GE90-115B": {"FPR": 1.61, "FBPR": 2.85},
    "Trent XWB-97": {"FPR": 1.5, "FBPR": 2.50},
    "GEnx-2B67/P": {"FPR": 1.5, "FBPR": 2.0},
    "LEAP-1B21": {"FPR": 1.38, "FBPR": 2.20},
    "LEAP-1B23": {"FPR": 1.39, "FBPR": 2.22},
    "LEAP-1B25": {"FPR": 1.40, "FBPR": 2.24},
    "LEAP-1B27": {"FPR": 1.41, "FBPR": 2.26},
    "LEAP-1B28": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28B2": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28B2C": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28BBJ1": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28BBJ1__2": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28BBJ2": {"FPR": 1.41, "FBPR": 2.26},
    "LEAP-1B28/28B1/28B2/28B3": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28/28B2/28B1/28B3": {"FPR": 1.42, "FBPR": 2.28},
    "LEAP-1B28/28B1/28B2/28B3__2": {"FPR": 1.42, "FBPR": 2.28},
    "PW1217G": {"FPR": 1.4, "FBPR": 2.02},
    "CF34-3B": {"FPR": 1.46, "FBPR": 2.35},
    "CF34-8C5": {"FPR": 1.52, "FBPR": 2.45},
    "CF34-8C5A1": {"FPR": 1.53, "FBPR": 2.46},
    "CF34-8C5A2": {"FPR": 1.54, "FBPR": 2.48},
    "CF34-8C5A3": {"FPR": 1.55, "FBPR": 2.50},
    "CF34-8C5B1": {"FPR": 1.50, "FBPR": 2.40},
    "CF34-8E5": {"FPR": 1.52, "FBPR": 2.45},
    "CF34-8E5__2": {"FPR": 1.52, "FBPR": 2.45},
    "CF34-8E5A1": {"FPR": 1.54, "FBPR": 2.48},
    "CF34-8E5A2HA": {"FPR": 1.5, "FBPR": 2.0},
    "CF34-10A16": {"FPR": 1.56, "FBPR": 2.52},
    "CF34-10A16/16-B": {"FPR": 1.56, "FBPR": 2.52},
    "CF34-10A16/B/C/D": {"FPR": 1.56, "FBPR": 2.52},
}

family_cycle_defaults = {
    "PW307": {"FPR": 1.40, "FBPR": 2.50},
    "PW4000": {"FPR": 1.55, "FBPR": 2.70},
    "CFM56-5B": {"FPR": 1.57, "FBPR": 2.54},
    "CFM56-7B": {"FPR": 1.58, "FBPR": 2.52},
    "GE90": {"FPR": 1.5, "FBPR": 2.5},
    "TRENT 900": {"FPR": 1.56, "FBPR": 2.71},
    "TRENT XWB": {"FPR": 1.5, "FBPR": 2.6},
    "GENX-1B": {"FPR": 1.50, "FBPR": 2.60},
    "GENX-2B": {"FPR": 1.46, "FBPR": 2.65},
    "LEAP-1B": {"FPR": 1.40, "FBPR": 2.24},
    "PW1000G": {"FPR": 1.32, "FBPR": 2.10},
    "CF34-3": {"FPR": 1.46, "FBPR": 2.35},
    "CF34-8": {"FPR": 1.53, "FBPR": 2.47},
    "CF34-10": {"FPR": 1.56, "FBPR": 2.52},
}


######MISSING DATA
#missing data added
from engine_ICAO_data_missing_high_BPR import (
    missing_icao_data,
    engine_diameter_m_missing,
    engine_cycle_defaults_missing,
)
icao_data.update(missing_icao_data)
engine_diameter_m.update(engine_diameter_m_missing)
engine_cycle_defaults.update(engine_cycle_defaults_missing)
######
from engine_missing_data_mid_bpr import missing_icao_data_mid_bpr, engine_diameter_m_missing_mid_bpr, engine_cycle_defaults_missing_mid_bpr
icao_data.update(missing_icao_data_mid_bpr)
engine_diameter_m.update(engine_diameter_m_missing_mid_bpr)
engine_cycle_defaults.update(engine_cycle_defaults_missing_mid_bpr)

def _normalize(name: str) -> str:
    return " ".join(name.upper().replace("_", " ").split())


def infer_family(name: str):
    n = _normalize(name)
    if n.startswith("PW307"):
        return "PW307"
    if n.startswith("PW40"):
        return "PW4000"
    if n.startswith("CFM56-5B"):
        return "CFM56-5B"
    if n.startswith("CFM56-7B"):
        return "CFM56-7B"
    if n.startswith("GE90"):
        return "GE90"
    if n.startswith("TRENT 97"):
        return "TRENT 900"
    if n.startswith("TRENT XWB"):
        return "TRENT XWB"
    if n.startswith("GENX-1B"):
        return "GENX-1B"
    if n.startswith("GENX-2B"):
        return "GENX-2B"
    if n.startswith("LEAP-1B"):
        return "LEAP-1B"
    if n.startswith("PW11") or n.startswith("PW12") or n.startswith("PW15") or n.startswith("PW19"):
        return "PW1000G"
    if n.startswith("CF34-3"):
        return "CF34-3"
    if n.startswith("CF34-8"):
        return "CF34-8"
    if n.startswith("CF34-10"):
        return "CF34-10"
    return None


def get_cycle_defaults(engine_name: str):
    if engine_name in engine_cycle_defaults:
        return deepcopy(engine_cycle_defaults[engine_name])
    family = infer_family(engine_name)
    if family and family in family_cycle_defaults:
        return deepcopy(family_cycle_defaults[family])
    return {"FPR": 1.50, "FBPR": 2.50}


def get_engine_diameter(engine_name: str):
    if engine_name in engine_diameter_m:
        return engine_diameter_m[engine_name]
    base = engine_name.split("__")[0]
    if base in engine_diameter_m:
        return engine_diameter_m[base]
    family = infer_family(engine_name)
    family_defaults = {
        "PW307": 1.0414,
        "PW4000": 2.3876,
        "CFM56-5B": 1.735,
        "CFM56-7B": 1.55,
        "GE90": 3.2512,
        "TRENT 900": 2.95,
        "TRENT XWB": 3.00,
        "GENX-1B": 2.819,
        "GENX-2B": 2.54,
        "LEAP-1B": 1.753,
        "PW1000G": 1.42,
        "CF34-3": 1.219,
        "CF34-8": 1.295,
        "CF34-10": 1.346,
    }
    if family in family_defaults:
        return family_defaults[family]
    return 1.50


def build_define_engine_kwargs(engine_name: str):
    row = icao_data[engine_name]
    cycle = get_cycle_defaults(engine_name)
    return {
        "BPR": row["bpr"],
        "CPR": row["opr"],
        "FPR": cycle["FPR"],
        "FBPR": cycle["FBPR"],
        "D": get_engine_diameter(engine_name),
        "design_thrust": row["rated_thrust_kN"] * 1000.0,
    }


def define_all_engines(define_engine_func):
    engine_objects = {}
    for name in icao_data:
        kwargs = build_define_engine_kwargs(name)
        engine_objects[name] = define_engine_func(**kwargs)
    return engine_objects

'''35,000ft:
        "Ta": 218.8,
        "Pa": 23800,'''
'''SL:
        "Ta": 288.15,
        "Pa": 101325,
        '''
def build_engines_config(engine_objects, default_conditions=None, t04_map=None):
    if default_conditions is None:
        default_conditions = {"M": 0.78, "Ta": 218.8, "Pa": 23800}
    if t04_map is None:
        t04_map = {}

    engines = {}
    for name, engine_obj in engine_objects.items():
        engines[name] = {
            "engine": engine_obj,
            "M": default_conditions["M"],
            "Ta": default_conditions["Ta"],
            "Pa": default_conditions["Pa"],
            "T04": t04_map.get(name, infer_default_t04(name)),
        }
    return engines


def infer_default_t04(engine_name: str):
    n = _normalize(engine_name)
    if n.startswith("JT3D") :
        return 1500
    if n.startswith("GE90") or n.startswith("TRENT") or n.startswith("GENX") or n.startswith("GEnx-1B7") or n.startswith("GE90-11"):
        return 1600
    if n.startswith("GE90-11") :
        return 1700
    if n.startswith("LEAP") :
        return 1700
    if n.startswith("LEAP-1") :
        return 2100
    if n.startswith("PW40") or n.startswith("PW1130G") or n.startswith("PW1133"):
        return 1400
    if n.startswith("CFM56") :
        return 1400
    if n.startswith("CF6") or n.startswith("CF34"):
        return 1400
    if n.startswith("PW11") or n.startswith("PW12") or n.startswith("PW14") or n.startswith("PW15") or n.startswith("PW19") or n.startswith("PW81"):
        return 1500

    if n.startswith("GEnx-1B75") or n.startswith("GEnx-1B74") or n.startswith("Trent XWB"):
        return 1500
        
    return 1200


def build_reference_dict(master, subkey):
    out = {}
    for name, row in master.items():
        if subkey in row:
            out[name] = deepcopy(row[subkey])
    return out


ICAO_fuel_flow = build_reference_dict(icao_data, "fuel_flow")


def compute_lto_fuel_burn_percent_difference(LTO_results, operating_points, icao_fuel_flow=None):
    if icao_fuel_flow is None:
        icao_fuel_flow = ICAO_fuel_flow

    differences = {}

    for name, results in LTO_results.items():
        differences[name] = {}

        if name not in icao_fuel_flow:
            continue

        total_model_fuel_burn = 0.0
        total_icao_fuel_burn = 0.0

        for point_name, point in operating_points.items():
            duration = point["time"]

            model_fuel_flow = results[point_name]["fuel_mass_flow"]
            model_fuel_burn = model_fuel_flow * duration

            icao_fuel_flow_value = icao_fuel_flow[name][point_name]
            icao_fuel_burn = icao_fuel_flow_value * duration

            if icao_fuel_burn == 0:
                percent_difference = None
            else:
                percent_difference = ((model_fuel_burn - icao_fuel_burn) / icao_fuel_burn) * 100.0

            differences[name][point_name] = percent_difference

            total_model_fuel_burn += model_fuel_burn
            total_icao_fuel_burn += icao_fuel_burn

        if total_icao_fuel_burn == 0:
            total_percent_difference = None
        else:
            total_percent_difference = ((total_model_fuel_burn - total_icao_fuel_burn) / total_icao_fuel_burn) * 100.0

        differences[name]["TOTAL"] = total_percent_difference

    return differences


def lto_fuel_burn_percent_difference_df(LTO_results, operating_points, icao_fuel_flow=None):
    differences = compute_lto_fuel_burn_percent_difference(LTO_results, operating_points, icao_fuel_flow)
    return pd.DataFrame(differences)


# -----------------------------------------------------------------------------
# Example usage
# -----------------------------------------------------------------------------
EXAMPLE_USAGE = r'''
from your_engine_module import define_engine
from all_engine_definitions_and_usage import (
    define_all_engines,
    build_engines_config,
    ICAO_fuel_flow,
    lto_fuel_burn_percent_difference_df,
)

# 1) Build all engine objects automatically
all_engine_objects = define_all_engines(define_engine)

# 2) Optionally override T04 for selected engines
custom_t04 = {
    "CFM56-5B1/3": 1400,
    "CFM56-7B20E": 1400,
    "GE90-115B": 1700,
    "PW307A": 1200,
    "Trent 970-84": 1700,
}

# 3) Build the same `engines = {...}` structure you already use
engines = build_engines_config(all_engine_objects, t04_map=custom_t04)

# 4) Run your model and get LTO_results exactly as before
# LTO_results = ...
# operating_points = ...

# 5) Compare against ICAO using the exact same fuel-burn logic pattern
comparison_df = lto_fuel_burn_percent_difference_df(
    LTO_results,
    operating_points,
    ICAO_fuel_flow,
)

print("\n")
print("=" * 90)
print("LTO FUEL BURN PERCENTAGE DIFFERENCE FROM ICAO")
print("=" * 90)
print(
    comparison_df.to_string(
        float_format=lambda x: "None" if pd.isna(x) else f"{x:+.2f}%"
    )
)
'''
