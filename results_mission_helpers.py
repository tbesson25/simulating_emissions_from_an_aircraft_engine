"""Helpers to compute simplified mission fuel burn for many engines.

This module extends the single-engine climb/cruise/descent workflow to all
engines in a shared `engines` dictionary and returns compact summary tables
that can be merged into your existing comparison views.

Expected existing data from the user's workflow:
- `engines`: dict with keys like engine name -> {"engine", "M", "Ta", "Pa", "T04"}
- `design_results`: dict keyed by engine name
- `area_results`: dict keyed by engine name
- `LTO_results`: dict keyed by engine name, each containing LTO operating-point
  results with `fuel_mass_flow`

Main outputs:
- mission_total_df: absolute fuel burn rows [kg]
- mission_rate_df: 1-hour cruise fuel burn rows [kg]
- mission_results also preserves detailed per-phase operating-point results and
  phase-point dictionaries so mission emissions can be computed later.
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Atmosphere and mission-point generators
# -----------------------------------------------------------------------------

def calculate_atmosphere(altitude: float) -> Tuple[float, float]:
    """Calculate ISA temperature and pressure."""
    T0 = 288.15
    P0 = 101325.0
    L = 0.0065
    R = 287.05
    g = 9.80665

    if altitude <= 11000:
        Ta = T0 - L * altitude
        Pa = P0 * (Ta / T0) ** (g / (R * L))
    else:
        Ta = 216.65
        Pa = 22632.06 * np.exp(-g * (altitude - 11000) / (R * Ta))
    return Ta, Pa


def generate_climb_profile(
    h_start: float,
    h_end: float,
    M_start: float,
    M_end: float,
    n_points: int,
    thrust_level: float,
    climb_rate: float,
) -> Dict[str, dict]:
    altitudes = np.linspace(h_start, h_end, n_points)
    mach_numbers = np.linspace(M_start, M_end, n_points)
    climb_points: Dict[str, dict] = {}

    for i in range(n_points - 1):
        dh = altitudes[i + 1] - altitudes[i]
        duration = dh / climb_rate
        climb_points[f"Climb_{i + 1}"] = {
            "altitude": float(altitudes[i]),
            "M": float(mach_numbers[i]),
            "thrust_level": thrust_level,
            "duration": float(duration),
        }
    return climb_points


def generate_cruise_profile(
    altitude: float,
    Mach: float,
    thrust_level: float,
    duration: float,
) -> Dict[str, dict]:
    return {
        "Cruise": {
            "altitude": altitude,
            "M": Mach,
            "thrust_level": thrust_level,
            "duration": duration,
        }
    }


def generate_descent_profile(
    h_start: float,
    h_end: float,
    M_start: float,
    M_end: float,
    n_points: int,
    thrust_level: float,
    descent_rate: float,
) -> Dict[str, dict]:
    altitudes = np.linspace(h_start, h_end, n_points)
    mach_numbers = np.linspace(M_start, M_end, n_points)
    descent_points: Dict[str, dict] = {}

    for i in range(n_points - 1):
        dh = altitudes[i] - altitudes[i + 1]
        duration = dh / descent_rate
        descent_points[f"Descent_{i + 1}"] = {
            "altitude": float(altitudes[i]),
            "M": float(mach_numbers[i]),
            "thrust_level": thrust_level,
            "duration": float(duration),
        }
    return descent_points


# -----------------------------------------------------------------------------
# Core simulation helpers
# -----------------------------------------------------------------------------

def simulate_flight_segment(
    operating_points: Dict[str, dict],
    design: dict,
    engine: dict,
    areas: dict,
    design_thrust: float,
    simulate_off_design_point,
) -> Tuple[Dict[str, dict], float]:
    """Run an off-design segment and return per-point results and total fuel burn."""
    results: Dict[str, dict] = {}
    total_fuel_burn = 0.0

    for name, point in operating_points.items():
        altitude = point["altitude"]
        M = point["M"]
        Ta, Pa = calculate_atmosphere(altitude)
        target_thrust = point["thrust_level"] * design_thrust

        result = simulate_off_design_point(
            target_thrust=target_thrust,
            M_off=M,
            Ta_off=Ta,
            Pa_off=Pa,
            design=design,
            engine=engine,
            areas=areas,
        )

        fuel_mass_flow = result["fuel_mass_flow"]
        duration = point["duration"]
        fuel_burn = fuel_mass_flow * duration

        enriched = dict(result)
        enriched["altitude"] = altitude
        enriched["Mach"] = M
        enriched["Ta"] = Ta
        enriched["Pa"] = Pa
        enriched["thrust_level"] = point["thrust_level"]
        enriched["target_thrust"] = target_thrust
        enriched["duration"] = duration
        enriched["fuel_burn"] = fuel_burn
        results[name] = enriched
        total_fuel_burn += fuel_burn

    return results, total_fuel_burn


def compute_lto_total_fuel_burn(
    lto_results: Dict[str, dict],
    operating_points: Dict[str, dict],
) -> float:
    """Compute total LTO fuel burn from existing LTO results and durations."""
    total = 0.0
    for point_name, point in operating_points.items():
        if point_name not in lto_results:
            continue
        total += lto_results[point_name]["fuel_mass_flow"] * point["time"]
    return total


# -----------------------------------------------------------------------------
# Multi-engine mission runner
# -----------------------------------------------------------------------------

def run_mission_for_all_engines(
    engines: Dict[str, dict],
    design_results: Dict[str, dict],
    area_results: Dict[str, dict],
    lto_results_all: Dict[str, dict],
    lto_operating_points: Dict[str, dict],
    simulate_off_design_point,
    climb_points: Optional[Dict[str, dict]] = None,
    cruise_points: Optional[Dict[str, dict]] = None,
    descent_points: Optional[Dict[str, dict]] = None,
) -> Dict[str, dict]:
    """Run simplified mission segments for all engines.

    Returns a dictionary keyed by engine name containing both fuel-burn totals
    and detailed per-phase results/points so mission emissions can be computed.
    """
    if climb_points is None:
        climb_points = generate_climb_profile(
            h_start=2000,
            h_end=11000,
            M_start=0.35,
            M_end=0.78,
            n_points=20,
            thrust_level=0.70,
            climb_rate=8.0,
        )
    if cruise_points is None:
        cruise_points = generate_cruise_profile(
            altitude=11000,
            Mach=0.78,
            thrust_level=0.60,
            duration=3600,
        )
    if descent_points is None:
        descent_points = generate_descent_profile(
            h_start=11000,
            h_end=2000,
            M_start=0.78,
            M_end=0.35,
            n_points=20,
            thrust_level=0.25,
            descent_rate=8.0,
        )

    mission_results: Dict[str, dict] = {}

    for name, data in engines.items():
        if name not in design_results or name not in area_results or name not in lto_results_all:
            continue

        engine = data["engine"]
        design = design_results[name]
        areas = area_results[name]
        design_thrust = engine["design_thrust"]

        climb_results, climb_fuel_burn = simulate_flight_segment(
            climb_points,
            design,
            engine,
            areas,
            design_thrust,
            simulate_off_design_point,
        )
        cruise_results, cruise_fuel_burn = simulate_flight_segment(
            cruise_points,
            design,
            engine,
            areas,
            design_thrust,
            simulate_off_design_point,
        )
        descent_results, descent_fuel_burn = simulate_flight_segment(
            descent_points,
            design,
            engine,
            areas,
            design_thrust,
            simulate_off_design_point,
        )
        lto_fuel_burn = compute_lto_total_fuel_burn(lto_results_all[name], lto_operating_points)

        mission_results[name] = {
            "lto_results": lto_results_all[name],
            "lto_operating_points": lto_operating_points,
            "climb_results": climb_results,
            "climb_points": climb_points,
            "cruise_results": cruise_results,
            "cruise_points": cruise_points,
            "descent_results": descent_results,
            "descent_points": descent_points,
            "lto_fuel_burn_kg": lto_fuel_burn,
            "climb_fuel_burn_kg": climb_fuel_burn,
            "cruise_fuel_burn_kg": cruise_fuel_burn,
            "descent_fuel_burn_kg": descent_fuel_burn,
            "total_mission_fuel_burn_kg": lto_fuel_burn + climb_fuel_burn + cruise_fuel_burn + descent_fuel_burn,
            "cruise_1h_fuel_burn_kg": cruise_fuel_burn,
        }

    return mission_results


# -----------------------------------------------------------------------------
# DataFrame builders for printing/merging into earlier tables
# -----------------------------------------------------------------------------

def build_mission_fuel_burn_df(mission_results: Dict[str, dict]) -> pd.DataFrame:
    """Return absolute mission fuel-burn rows in kg, one engine per column."""
    rows = {
        "LTO_FUEL_BURN_kg": {},
        "CLIMB_FUEL_BURN_kg": {},
        "CRUISE_1H_FUEL_BURN_kg": {},
        "DESCENT_FUEL_BURN_kg": {},
        "TOTAL_MISSION_FUEL_BURN_kg": {},
    }

    for name, result in mission_results.items():
        rows["LTO_FUEL_BURN_kg"][name] = result.get("lto_fuel_burn_kg")
        rows["CLIMB_FUEL_BURN_kg"][name] = result.get("climb_fuel_burn_kg")
        rows["CRUISE_1H_FUEL_BURN_kg"][name] = result.get("cruise_1h_fuel_burn_kg")
        rows["DESCENT_FUEL_BURN_kg"][name] = result.get("descent_fuel_burn_kg")
        rows["TOTAL_MISSION_FUEL_BURN_kg"][name] = result.get("total_mission_fuel_burn_kg")

    return pd.DataFrame(rows).T


def build_combined_summary_with_mission_df(
    fuel_burn_percent_df: pd.DataFrame,
    emissions_percent_df: pd.DataFrame,
    mission_fuel_burn_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Build compact summary rows for final comparison tables."""
    engine_names = []
    for col in fuel_burn_percent_df.columns:
        if col not in engine_names:
            engine_names.append(col)
    for col in emissions_percent_df.columns:
        if col not in engine_names:
            engine_names.append(col)
    if mission_fuel_burn_df is not None:
        for col in mission_fuel_burn_df.columns:
            if col not in engine_names:
                engine_names.append(col)

    rows = {
        "TOTAL_FUEL_BURN_%": {},
        "NOx_%": {},
        "CO_%": {},
        "HC_%": {},
    }

    for name in engine_names:
        rows["TOTAL_FUEL_BURN_%"][name] = (
            fuel_burn_percent_df.loc["TOTAL", name]
            if "TOTAL" in fuel_burn_percent_df.index and name in fuel_burn_percent_df.columns
            else None
        )
        rows["NOx_%"][name] = (
            emissions_percent_df.loc["NOx", name]
            if "NOx" in emissions_percent_df.index and name in emissions_percent_df.columns
            else None
        )
        rows["CO_%"][name] = (
            emissions_percent_df.loc["CO", name]
            if "CO" in emissions_percent_df.index and name in emissions_percent_df.columns
            else None
        )
        rows["HC_%"][name] = (
            emissions_percent_df.loc["HC", name]
            if "HC" in emissions_percent_df.index and name in emissions_percent_df.columns
            else None
        )

    if mission_fuel_burn_df is not None:
        rows["CRUISE_1H_FUEL_BURN_kg"] = {}
        rows["TOTAL_MISSION_FUEL_BURN_kg"] = {}
        for name in engine_names:
            rows["CRUISE_1H_FUEL_BURN_kg"][name] = (
                mission_fuel_burn_df.loc["CRUISE_1H_FUEL_BURN_kg", name]
                if "CRUISE_1H_FUEL_BURN_kg" in mission_fuel_burn_df.index and name in mission_fuel_burn_df.columns
                else None
            )
            rows["TOTAL_MISSION_FUEL_BURN_kg"][name] = (
                mission_fuel_burn_df.loc["TOTAL_MISSION_FUEL_BURN_kg", name]
                if "TOTAL_MISSION_FUEL_BURN_kg" in mission_fuel_burn_df.index and name in mission_fuel_burn_df.columns
                else None
            )

    return pd.DataFrame(rows).T.reindex(columns=engine_names)
