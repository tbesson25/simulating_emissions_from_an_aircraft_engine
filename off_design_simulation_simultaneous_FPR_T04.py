from off_design_simultaneous_solver import solve_off_design


def simulate3_off_design_point(
    target_thrust,
    M_off,
    Ta_off,
    Pa_off,
    design,
    engine,
    areas,
    initial_guess=(1.3, 1400)
):

    result = solve_off_design(
        target_thrust=target_thrust,
        M_off=M_off,
        Ta_off=Ta_off,
        Pa_off=Pa_off,
        design=design,
        engine=engine,
        areas=areas,
        initial_guess=initial_guess
    )

    return result