#Dictionary of operating points
'''
The operating points are defined using prescribed thrust fractions relative to the design-point thrust. The required turbine inlet temperature is subsequently determined iteratively such that the off-design engine produces the prescribed thrust.
'''
#operating_points is LTO cycle only
operating_points = {
    "takeoff": {
        "altitude": 0,
        "M": 0.2,
        "thrust_level": 1.00,
        "time": 0.7*60,
    },

    "climbout": {
        "altitude": 915,
        "M": 0.25,
        "thrust_level": 0.85,
        "time": 2.2*60,
    },

    "approach": {
        "altitude": 915, #same as climbout?
        "M": 0.2,
        "thrust_level": 0.30,
        "time": 4*60,
    },

    "idle": {
        "altitude": 0,
        "M": 0.2,
        "thrust_level": 0.07,
        "time": 26 * 60,
    },    
}


cruise_operating_points = {

    "cruise": {
        "altitude": 10668,   # 35,000 ft
        "M": 0.70,
        "thrust_level": 0.75,
        "time": 60*60,           #for an hour of cruise
    },
}
