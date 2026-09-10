"""Patch data for missing mid-bypass turbofans in the same `icao_data` format.

Rule applied:
- If repeated rows have the same engine name AND same (bpr, opr, rated_thrust_kN),
  keep only one.
- If repeated rows have the same engine name but different (bpr, opr, rated_thrust_kN),
  keep them as separate entries with suffixes like __2, __3, ...

This file is intended to be merged into an existing `icao_data` dictionary.
"""

missing_icao_data_mid_bpr = {
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
        "fuel_flow": {"takeoff": 0.875, "climbout": 0.727, "approach": 0.26, "idle": 0.091, "lto_cycle": 338},
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
        "fuel_flow": {"takeoff": 4.69, "climbout": 3.67, "approach": 1.13, "idle": 0.38, "lto_cycle": 1546},
        "hc_ei": {"takeoff": 0.04, "climbout": 0.03, "approach": 0.06, "idle": 4.24, "lto_total_g": 2559},
        "co_ei": {"takeoff": 0.08, "climbout": 0.07, "approach": 1.98, "idle": 39.11, "lto_total_g": 23858},
        "nox_ei": {"takeoff": 50.34, "climbout": 35.98, "approach": 16.5, "idle": 5.19, "lto_total_g": 34888},
    },
    "GE90-110B1": {
        "manufacturer": "General Electric Company",
        "bpr": 7.2,
        "opr": 40.6,
        "rated_thrust_kN": 492.7,
        "fuel_flow": {"takeoff": 4.221, "climbout": 3.37, "approach": 1.024, "idle": 0.332, "lto_cycle": 1386},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.03, "approach": 0.04, "idle": 6.32, "lto_total_g": 3300},
        "co_ei": {"takeoff": 0.05, "climbout": 0.5, "approach": 2.94, "idle": 44.12, "lto_total_g": 23793},
        "nox_ei": {"takeoff": 44.93, "climbout": 32.57, "approach": 15.4, "idle": 5.02, "lto_total_g": 28841},
    },
    "GE90-110B1__2": {
        "manufacturer": "General Electric Company",
        "bpr": 7.3,
        "opr": 40.4,
        "rated_thrust_kN": 492.6,
        "fuel_flow": {"takeoff": 4.226, "climbout": 3.375, "approach": 1.029, "idle": 0.334, "lto_cycle": 1391},
        "hc_ei": {"takeoff": 0.03, "climbout": 0.02, "approach": 0.05, "idle": 3.87, "lto_total_g": 2043},
        "co_ei": {"takeoff": 0.13, "climbout": 0.14, "approach": 2.5, "idle": 35.72, "lto_total_g": 19317},
        "nox_ei": {"takeoff": 45.25, "climbout": 34.39, "approach": 15.53, "idle": 5.42, "lto_total_g": 30010},
    },
    "GE90-110B1__3": {
        "manufacturer": "General Electric Company",
        "bpr": 7.3,
        "opr": 39.7,
        "rated_thrust_kN": 492.6,
        "fuel_flow": {"takeoff": 4.32, "climbout": 3.47, "approach": 1.08, "idle": 0.37, "lto_cycle": 1479},
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
}
#removed
'''    "Trent 972-84": {
        "manufacturer": "Rolls-Royce plc",
        "bpr": 7.5,
        "opr": 38.6,
        "rated_thrust_kN": 345.9,
        "fuel_flow": {"takeoff": 2.69, "climbout": 2.23, "approach": 0.75, "idle": 0.27, "lto_cycle": 1009},
        "hc_ei": {"takeoff": 0.0, "climbout": 0.0, "approach": 0.0, "idle": 0.24, "lto_total_g": 101},
        "co_ei": {"takeoff": 0.4, "climbout": 0.3, "approach": 1.4, "idle": 15.94, "lto_total_g": 7099},
        "nox_ei": {"takeoff": 38.8, "climbout": 29.6, "approach": 11.8, "idle": 5.0, "lto_total_g": 17327},
    },'''
"""Patch data for missing mid-bypass turbofans in engine_definition format.

This file adds:
- engine_diameter_m entries
- engine_cycle_defaults entries

It is intended to be merged into an existing engine_definition module state.
Values follow the user's current conventions:
- diameters are family/public-reference defaults or consistent family placeholders
- FPR / FBPR are engineering defaults / estimates aligned with existing patterns
- duplicate ICAO rows with distinct cycle points use suffixed names like __2, __3
"""

engine_diameter_m_missing_mid_bpr = {
    "CFM56-5B5/3": 1.735,
    "CFM56-5B8/3": 1.735,
    "CF34-3B": 1.219,
    "CF34-3B/-3B1": 1.219,
    "CF34-3A/A1/A2/B1/B2": 1.219,
    "GE90-115B": 3.2512,
    "GE90-115B__2": 3.2512,
    "GE90-115B__3": 3.2512,
    "GE90-110B1": 3.2512,
    "GE90-110B1__2": 3.2512,
    "GE90-110B1__3": 3.2512,
    "Trent 970-84": 2.95,
    "Trent 972-84": 2.95,
}


engine_cycle_defaults_missing_mid_bpr = {
    "CFM56-5B5/3": {"FPR": 1.50, "FBPR": 2.00},
    "CFM56-5B8/3": {"FPR": 1.50, "FBPR": 2.00},
    "CF34-3B": {"FPR": 1.46, "FBPR": 2.35},
    "CF34-3B/-3B1": {"FPR": 1.46, "FBPR": 2.35},
    "CF34-3A/A1/A2/B1/B2": {"FPR": 1.46, "FBPR": 2.35},
    "GE90-115B": {"FPR": 1.61, "FBPR": 2.85},
    "GE90-115B__2": {"FPR": 1.61, "FBPR": 2.85},
    "GE90-115B__3": {"FPR": 1.5, "FBPR": 2.8},
    "GE90-110B1": {"FPR": 1.60, "FBPR": 2.80},
    "GE90-110B1__2": {"FPR": 1.6, "FBPR": 2.80},
    "GE90-110B1__3": {"FPR": 1.50, "FBPR": 2.60},
    "Trent 970-84": {"FPR": 1.3, "FBPR": 2.6},
    "Trent 972-84": {"FPR": 1.4, "FBPR": 2.6},
}


