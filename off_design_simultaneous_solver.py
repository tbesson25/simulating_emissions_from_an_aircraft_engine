
"""
Simultaneously solves for FPR and T04.
Equation 1:
    m_core_A4 - m_core_A9 = 0
Equation 2:
    Thrust - target_thrust = 0
"""
import numpy as np
from scipy.optimize import root

from off_design import run_cumpsty_off_design


def off_design_residuals(
    variables,
    target_thrust,
    M_off,
    Ta_off,
    Pa_off,
    design,
    engine,
    areas
):
    FPR_off, T04_off = variables
    # Run the off-design cycle
    try:
        result = run_cumpsty_off_design(
            FPR=FPR_off,
            M_off=M_off,
            Ta_off=Ta_off,
            Pa_off=Pa_off,
            T04_off=T04_off,
            design=design,
            engine=engine,
            areas=areas
        )
    except Exception:
        return [1e6, 1e6]
    # Mass-flow matching residual
    m4 = result["mass_flow_core_A4"]
    m9 = result["mass_flow_core_A9"]
    mass_residual = m4 - m9
    # Thrust residual
    thrust_residual = result["Thrust"] - target_thrust
    return [
        mass_residual,
        thrust_residual / 1000   # scaling helps numerical convergence
    ]

def solve_off_design(
    target_thrust,
    M_off,
    Ta_off,
    Pa_off,
    design,
    engine,
    areas,
    initial_guess=(1.3, 1400)
):
    solution = root(
        off_design_residuals,
        initial_guess,
        args=(
            target_thrust,
            M_off,
            Ta_off,
            Pa_off,
            design,
            engine,
            areas
        )
    )
    if not solution.success:
        raise ValueError(
            f"Off-design solver failed: {solution.message}"
        )
    FPR_off, T04_off = solution.x
    # Check physical limits
    if FPR_off <= 1.0:
        raise ValueError(
            f"Non-physical FPR obtained: {FPR_off}"
        )
    if T04_off <= 0:
        raise ValueError(
            f"Non-physical T04 obtained: {T04_off}"
        )
    # Run once more using converged values
    result = run_cumpsty_off_design(
        FPR=FPR_off,
        M_off=M_off,
        Ta_off=Ta_off,
        Pa_off=Pa_off,
        T04_off=T04_off,
        design=design,
        engine=engine,
        areas=areas
    )
    result["FPR"] = FPR_off
    result["T04"] = T04_off
    result["target_thrust"] = target_thrust
    return result