#Loop over the operating points, using the off-design and simultaneous iteration on FPR and T04

from atmosphere import calculate_atmosphere
from off_design_simulation_FPR_then_T04_iter import simulate2_off_design_point
from off_design_simulation_simultaneous_FPR_T04 import simulate3_off_design_point

def simulate_operating_points(
    operating_points,
    design,
    engine,
    areas,
    design_thrust
):
    operating_results = {}
    for name, point in operating_points.items():
        print(
            f"\n  {name.upper():<10}"
            f" | h = {point['altitude']:>6.0f} m"
            f" | M = {point['M']:.2f}"
            f" | target thrust = "
            f"{point['thrust_level'] * design_thrust:.1f} N"
        )
       
        # Atmospheric conditions
        Ta, Pa = calculate_atmosphere(point["altitude"])
        
        # Off-design engine simulation
        try:
            result = simulate3_off_design_point(
                target_thrust=point["thrust_level"] * design_thrust,
                M_off=point["M"],
                Ta_off=Ta,
                Pa_off=Pa,
                design=design,
                engine=engine,
                areas=areas,
            )

        except Exception as e:
            print(f"FAILED at {name}: {e}")
            raise
        '''
        result = simulate3_off_design_point( #with simultaneous iteration #change from simulate2 
            target_thrust=point["thrust_level"] * design_thrust,
            M_off=point["M"],
            Ta_off=Ta,
            Pa_off=Pa,
            design=design,
            engine=engine,
            areas=areas,
        )
        '''
        # Store flight-condition information
        result["altitude"] = point["altitude"]
        result["Mach"] = point["M"]
        result["Ta"] = Ta
        result["Pa"] = Pa
        result["thrust_level"] = point["thrust_level"]
        operating_results[name] = result

    return operating_results