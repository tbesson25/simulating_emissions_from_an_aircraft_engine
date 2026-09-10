"""Helpers to compute mission emissions for many engines.

This module computes species-specific emissions for LTO, climb, cruise, and
descent using the same calculate_engine_emissions function already used for LTO.
It adapts mission operating-point dictionaries that use ``duration`` so they can
be consumed by emissions functions expecting ``time``.

Expected inputs
---------------
- mission_results[name] should contain:
    {
        "lto_results": <dict>,
        "lto_operating_points": <dict>,
        "climb_results": <dict>,
        "climb_points": <dict>,
        "cruise_results": <dict>,
        "cruise_points": <dict>,
        "descent_results": <dict>,
        "descent_points": <dict>,
    }
- icao_ei_by_engine[name]:
    {
        "NOx": {"idle": ..., ...},
        "CO":  {...},
        "HC":  {...},
    }
- p3t3_reference_by_engine[name] is optional and, if provided, should be:
    {
        "NOx": <reference_data>,
        "CO":  <reference_data>,
        "HC":  <reference_data>,
    }
"""

from __future__ import annotations

from typing import Dict, Optional
import pandas as pd


SPECIES_LIST = ["NOx", "CO", "HC"]


def _ensure_time_key(points: Dict[str, dict]) -> Dict[str, dict]:
    """Return a copy of operating points with a ``time`` key available.

    LTO points often use ``time`` already, while mission segments commonly use
    ``duration``. This helper makes both compatible with emissions functions.
    """
    normalized: Dict[str, dict] = {}
    for name, payload in (points or {}).items():
        row = dict(payload)
        if "time" not in row:
            row["time"] = row.get("duration", 0.0)
        normalized[name] = row
    return normalized


def _sum_species_mass(species_results: Dict[str, dict]) -> float:
    return sum(x.get("emission_mass", 0.0) for x in species_results.values())


def build_segment_total_emissions(segment_emissions: Dict[str, dict]) -> Dict[str, float]:
    """Build total NOx/CO/HC mass [kg] for one segment result dict.

    Expected shape:
        {
            "NOx": {point_name: {"emission_mass": ...}, ...},
            "CO":  {...},
            "HC":  {...},
        }
    """
    return {
        "NOx_kg": _sum_species_mass(segment_emissions.get("NOx", {})),
        "CO_kg": _sum_species_mass(segment_emissions.get("CO", {})),
        "HC_kg": _sum_species_mass(segment_emissions.get("HC", {})),
    }


def calculate_emissions_for_segment(
    engine_name: str,
    operating_results: Dict[str, dict],
    operating_points: Dict[str, dict],
    calculate_engine_emissions_func,
    ICAO_EI: Dict[str, dict],
    P3T3_reference_by_species: Optional[Dict[str, dict]] = None,
):
    """Call the user's engine-emissions function for one mission segment.

    Supports both function signatures:
    1) calculate_engine_emissions(..., ICAO_EI, P3T3_reference_by_species=...)
    2) calculate_engine_emissions(..., ICAO_EI)
    """
    normalized_points = _ensure_time_key(operating_points)

    try:
        return calculate_engine_emissions_func(
            engine_name=engine_name,
            operating_results=operating_results,
            operating_points=normalized_points,
            ICAO_EI=ICAO_EI,
            P3T3_reference_by_species=P3T3_reference_by_species,
        )
    except TypeError:
        return calculate_engine_emissions_func(
            engine_name=engine_name,
            operating_results=operating_results,
            operating_points=normalized_points,
            ICAO_EI=ICAO_EI,
        )


def run_mission_emissions_for_all_engines(
    mission_results: Dict[str, dict],
    icao_ei_by_engine: Dict[str, dict],
    calculate_engine_emissions_func,
    p3t3_reference_by_engine: Optional[Dict[str, Dict[str, dict]]] = None,
) -> Dict[str, dict]:
    """Compute emissions for LTO/climb/cruise/descent for all engines.

    Returns
    -------
    all_results : dict
        {
            engine_name: {
                "LTO": <segment emissions>,
                "CLIMB": <segment emissions>,
                "CRUISE": <segment emissions>,
                "DESCENT": <segment emissions>,
            }
        }
    """
    all_results: Dict[str, dict] = {}

    for name, payload in mission_results.items():
        if name not in icao_ei_by_engine:
            continue

        icao_ei = icao_ei_by_engine[name]
        species_refs = None if p3t3_reference_by_engine is None else p3t3_reference_by_engine.get(name)

        engine_bundle: Dict[str, dict] = {}

        if "lto_results" in payload and "lto_operating_points" in payload:
            engine_bundle["LTO"] = calculate_emissions_for_segment(
                engine_name=name,
                operating_results=payload["lto_results"],
                operating_points=payload["lto_operating_points"],
                calculate_engine_emissions_func=calculate_engine_emissions_func,
                ICAO_EI=icao_ei,
                P3T3_reference_by_species=species_refs,
            )

        if "climb_results" in payload and "climb_points" in payload:
            engine_bundle["CLIMB"] = calculate_emissions_for_segment(
                engine_name=name,
                operating_results=payload["climb_results"],
                operating_points=payload["climb_points"],
                calculate_engine_emissions_func=calculate_engine_emissions_func,
                ICAO_EI=icao_ei,
                P3T3_reference_by_species=species_refs,
            )

        if "cruise_results" in payload and "cruise_points" in payload:
            engine_bundle["CRUISE"] = calculate_emissions_for_segment(
                engine_name=name,
                operating_results=payload["cruise_results"],
                operating_points=payload["cruise_points"],
                calculate_engine_emissions_func=calculate_engine_emissions_func,
                ICAO_EI=icao_ei,
                P3T3_reference_by_species=species_refs,
            )

        if "descent_results" in payload and "descent_points" in payload:
            engine_bundle["DESCENT"] = calculate_emissions_for_segment(
                engine_name=name,
                operating_results=payload["descent_results"],
                operating_points=payload["descent_points"],
                calculate_engine_emissions_func=calculate_engine_emissions_func,
                ICAO_EI=icao_ei,
                P3T3_reference_by_species=species_refs,
            )

        all_results[name] = engine_bundle

    return all_results


def build_mission_emissions_summary_df(all_mission_emissions: Dict[str, dict]) -> pd.DataFrame:
    """Build a summary DataFrame with LTO, per-phase, and total mission kg rows.

    Rows produced include:
    - NOx_kg, CO_kg, HC_kg               (kept as LTO totals for compatibility)
    - LTO_NOx_kg, LTO_CO_kg, LTO_HC_kg
    - CLIMB_NOx_kg, CLIMB_CO_kg, CLIMB_HC_kg
    - CRUISE_NOx_kg, CRUISE_CO_kg, CRUISE_HC_kg
    - DESCENT_NOx_kg, DESCENT_CO_kg, DESCENT_HC_kg
    - TOTAL_MISSION_NOx_kg, TOTAL_MISSION_CO_kg, TOTAL_MISSION_HC_kg
    """
    table: Dict[str, Dict[str, float]] = {}

    for name, bundle in all_mission_emissions.items():
        rows: Dict[str, float] = {}

        lto = build_segment_total_emissions(bundle.get("LTO", {})) if "LTO" in bundle else None
        climb = build_segment_total_emissions(bundle.get("CLIMB", {})) if "CLIMB" in bundle else None
        cruise = build_segment_total_emissions(bundle.get("CRUISE", {})) if "CRUISE" in bundle else None
        descent = build_segment_total_emissions(bundle.get("DESCENT", {})) if "DESCENT" in bundle else None

        if lto is not None:
            rows["NOx_kg"] = lto["NOx_kg"]
            rows["CO_kg"] = lto["CO_kg"]
            rows["HC_kg"] = lto["HC_kg"]
            rows["LTO_NOx_kg"] = lto["NOx_kg"]
            rows["LTO_CO_kg"] = lto["CO_kg"]
            rows["LTO_HC_kg"] = lto["HC_kg"]
        else:
            rows["NOx_kg"] = 0.0
            rows["CO_kg"] = 0.0
            rows["HC_kg"] = 0.0
            rows["LTO_NOx_kg"] = 0.0
            rows["LTO_CO_kg"] = 0.0
            rows["LTO_HC_kg"] = 0.0

        if climb is not None:
            rows["CLIMB_NOx_kg"] = climb["NOx_kg"]
            rows["CLIMB_CO_kg"] = climb["CO_kg"]
            rows["CLIMB_HC_kg"] = climb["HC_kg"]
        else:
            rows["CLIMB_NOx_kg"] = 0.0
            rows["CLIMB_CO_kg"] = 0.0
            rows["CLIMB_HC_kg"] = 0.0

        if cruise is not None:
            rows["CRUISE_NOx_kg"] = cruise["NOx_kg"]
            rows["CRUISE_CO_kg"] = cruise["CO_kg"]
            rows["CRUISE_HC_kg"] = cruise["HC_kg"]
        else:
            rows["CRUISE_NOx_kg"] = 0.0
            rows["CRUISE_CO_kg"] = 0.0
            rows["CRUISE_HC_kg"] = 0.0

        if descent is not None:
            rows["DESCENT_NOx_kg"] = descent["NOx_kg"]
            rows["DESCENT_CO_kg"] = descent["CO_kg"]
            rows["DESCENT_HC_kg"] = descent["HC_kg"]
        else:
            rows["DESCENT_NOx_kg"] = 0.0
            rows["DESCENT_CO_kg"] = 0.0
            rows["DESCENT_HC_kg"] = 0.0

        rows["TOTAL_MISSION_NOx_kg"] = (
            rows["LTO_NOx_kg"]
            + rows["CLIMB_NOx_kg"]
            + rows["CRUISE_NOx_kg"]
            + rows["DESCENT_NOx_kg"]
        )
        rows["TOTAL_MISSION_CO_kg"] = (
            rows["LTO_CO_kg"]
            + rows["CLIMB_CO_kg"]
            + rows["CRUISE_CO_kg"]
            + rows["DESCENT_CO_kg"]
        )
        rows["TOTAL_MISSION_HC_kg"] = (
            rows["LTO_HC_kg"]
            + rows["CLIMB_HC_kg"]
            + rows["CRUISE_HC_kg"]
            + rows["DESCENT_HC_kg"]
        )

        table[name] = rows

    df = pd.DataFrame(table)
    preferred_order = [
        "NOx_kg", "CO_kg", "HC_kg",
        "LTO_NOx_kg", "LTO_CO_kg", "LTO_HC_kg",
        "CLIMB_NOx_kg", "CLIMB_CO_kg", "CLIMB_HC_kg",
        "CRUISE_NOx_kg", "CRUISE_CO_kg", "CRUISE_HC_kg",
        "DESCENT_NOx_kg", "DESCENT_CO_kg", "DESCENT_HC_kg",
        "TOTAL_MISSION_NOx_kg", "TOTAL_MISSION_CO_kg", "TOTAL_MISSION_HC_kg",
    ]
    return df.reindex(preferred_order)
