"""This script shows BPR-grouped fuel-burn and emissions summaries results for some chosen engines. (can change to all engines cf line 98)

This script keeps ONE final printed view grouped by BPR, containing:
- metadata rows
- LTO fuel-burn percent difference rows
- LTO emissions percent difference rows
- LTO emissions absolute kg rows
- mission fuel-burn absolute kg rows
- mission emissions absolute kg rows

Assumptions
-----------
You already have these available in your project:
- define_all_engines, build_engines_config, ICAO_fuel_flow
- define_engine
- operating_points, simulate_operating_points
- run_cumpsty_cycle
- calculate_engine_areas
- simulate3_off_design_point
- icao_data
- engine_diameter_m, engine_cycle_defaults
- results_table_helpers_all.build_and_print_combined_summary_by_bpr
- results_mission_fuel_burn_helpers.run_mission_for_all_engines
- results_mission_fuel_burn_helpers.build_mission_fuel_burn_df
- results_multi_engine_emissions_helpers:
    * calculate_emissions_for_all_engines
    * build_total_emissions_kg_df
    * build_icao_total_emissions_kg_df
    * compute_total_lto_emissions_percent_difference_df
    * calculate_engine_emissions
    * build_P3T3_reference
- mission_emissions_helpers:
    * run_mission_emissions_for_all_engines
    * build_mission_emissions_summary_df
    
All printed results are grouped by BPR.
"""

from __future__ import annotations

import pandas as pd

# ============================================================
# ENGINE SETUP
# ============================================================
from engine_definition import (
    define_all_engines,
    build_engines_config,
    ICAO_fuel_flow,
    lto_fuel_burn_percent_difference_df,
    engine_diameter_m,
    engine_cycle_defaults,
)
from engine_parameters import define_engine
from engine_ICAO_data import icao_data
#missing data added
from engine_ICAO_data_missing_high_BPR import (
    missing_icao_data,
    engine_diameter_m_missing,
    engine_cycle_defaults_missing,
)
icao_data.update(missing_icao_data)
engine_diameter_m.update(engine_diameter_m_missing)
engine_cycle_defaults.update(engine_cycle_defaults_missing)
####


all_engine_objects = define_all_engines(define_engine)
custom_t04 = {
    "CFM56-5B1/3": 1400,
    "CFM56-5B9/3": 1500,
    "CFM56-7B20E": 1400,
    "GE90-115B": 1700,
    "GE90-110B1": 1700,
    "PW307A": 1400,
    "Trent 970-84": 1500,
    "GE90-115B__2": 1700,
    "GE90-115B": 1700,
    "GE90-110B1": 1700,
    "GE90-110B1__2": 1700,
    "GEnx-2B67/P":1500,
    "Trent XWB-97":1500,
    "LEAP-1B28BBJ1":1400,
    "LEAP-1B28B2C":1400,
    "GEnx-1B76/P2":1500,
    "GEnx-1B76A/P2":1500,
    "GEnx-2B67/P":1500,
    "GEnx-1B75/P2":1500,
    "GEnx-1B75/P2__2":1500,
    "PW1431GH-JM":1400,
    "PW1129G-JM":1400,
    "PW1428GH-JM":1400,
    "PW1127G1-JM":1400,
    "PW1122G-JM":1400,
}
engines = build_engines_config(all_engine_objects, t04_map=custom_t04)

# Select only the engines to simulate (Remove lines 99-109 if want to see all engines)
selected_engines = [
    "CFM56-5B1/3",
    "GE90-115B",
    "Trent XWB-97",
]

engines = {
    name: engines[name]
    for name in selected_engines
    if name in engines
}
# ============================================================
# LTO DESIGN / AREA / LTO RESULTS
# ============================================================
from operating_points import operating_points
from operating_points_simulation import simulate_operating_points
from cumpsty_cycle import run_cumpsty_cycle
from engine_areas import calculate_engine_areas


def build_design_results(engines_dict):
    design_results_local = {}
    for name, data in engines_dict.items():
        engine = data["engine"]
        design_thrust = engine["design_thrust"]

        print("")
        print("=" * 70)
        print(f"DESIGN POINT: {name}")
        print("=" * 70)

        design = run_cumpsty_cycle(
            M=data["M"],
            Ta=data["Ta"],
            Pa=data["Pa"],
            T04=data["T04"],
            engine=engine,
            Thrust=design_thrust,
        )
        design_results_local[name] = design
    return design_results_local



def build_area_results(engines_dict, design_results_local):
    area_results_local = {}
    for name, data in engines_dict.items():
        print("\n")
        print("=" * 60)
        print(f"ENGINE AREAS: {name}")
        print("=" * 60)

        areas = calculate_engine_areas(
            design_results_local[name],
            data["engine"],
            Pa=data["Pa"],
        )
        area_results_local[name] = areas
    return area_results_local



def build_lto_results(engines_dict, design_results_local, area_results_local):
    lto_results_local = {}
    for name, data in engines_dict.items():
        engine = data["engine"]
        design_thrust = engine["design_thrust"]

        print("")
        print("=" * 60)
        print(f"LTO SIMULATION: {name}")
        print("=" * 60)

        results = simulate_operating_points(
            operating_points=operating_points,
            design=design_results_local[name],
            engine=engine,
            areas=area_results_local[name],
            design_thrust=design_thrust,
        )
        lto_results_local[name] = results
    return lto_results_local


design_results = build_design_results(engines)
area_results = build_area_results(engines, design_results)
LTO_results = build_lto_results(engines, design_results, area_results)

LTO_fuel_burn_percent_difference_df = lto_fuel_burn_percent_difference_df(
    LTO_results,
    operating_points,
    ICAO_fuel_flow,
)


# ============================================================
# LTO EMISSIONS WITH SPECIES-SPECIFIC P3T3
# ============================================================
#use results_multi_engine_emissions_helpers _include_humidity if want to include humidity factor in NOx calculation
from results_multi_engine_emissions_helpers import (
    calculate_emissions_for_all_engines,
    build_total_emissions_kg_df,
    build_icao_total_emissions_kg_df,
    compute_total_lto_emissions_percent_difference_df,
    calculate_engine_emissions,
    build_P3T3_reference,
)

ICAO_EI_by_engine, P3T3_reference_by_engine, all_engine_emissions = (
    calculate_emissions_for_all_engines(
        engines=engines,
        lto_results=LTO_results,
        operating_points=operating_points,
        icao_data=icao_data,
        calculate_engine_emissions_func=calculate_engine_emissions,
        build_P3T3_reference_func=build_P3T3_reference,
        species_list=["NOx", "CO", "HC"],
    )
)

LTO_total_emissions_df = build_total_emissions_kg_df(all_engine_emissions)
ICAO_total_emissions_df = build_icao_total_emissions_kg_df(
    engine_names=list(LTO_total_emissions_df.columns),
    icao_data=icao_data,
)
LTO_emissions_percent_difference_df = (
    compute_total_lto_emissions_percent_difference_df(
        model_total_emissions_kg_df=LTO_total_emissions_df,
        icao_total_emissions_kg_df=ICAO_total_emissions_df,
    )
)


# ============================================================
# MISSION FUEL BURN
# ============================================================
from off_design_simulation_simultaneous_FPR_T04 import simulate3_off_design_point
from results_mission_helpers import (
    run_mission_for_all_engines,
    build_mission_fuel_burn_df,
)

mission_results = run_mission_for_all_engines(
    engines=engines,
    design_results=design_results,
    area_results=area_results,
    lto_results_all=LTO_results,
    lto_operating_points=operating_points,
    simulate_off_design_point=simulate3_off_design_point,
)
mission_fuel_burn_df = build_mission_fuel_burn_df(mission_results)


# ============================================================
# MISSION EMISSIONS
# ============================================================
from results_mission_emissions_helpers import (
    run_mission_emissions_for_all_engines,
    build_mission_emissions_summary_df,
)

all_mission_emissions = run_mission_emissions_for_all_engines(
    mission_results=mission_results,
    icao_ei_by_engine=ICAO_EI_by_engine,
    calculate_engine_emissions_func=calculate_engine_emissions,
    p3t3_reference_by_engine=P3T3_reference_by_engine,
)
mission_emissions_summary_df = build_mission_emissions_summary_df(all_mission_emissions)


# ============================================================
# FINAL SINGLE COMBINED TABLE - 
# ============================================================
from results_table_helpers_all import build_and_print_combined_summary_by_bpr

combined_summary_df = build_and_print_combined_summary_by_bpr(
    fuel_burn_percent_df=LTO_fuel_burn_percent_difference_df,
    emissions_percent_df=LTO_emissions_percent_difference_df,
    emissions_kg_df=LTO_total_emissions_df,
    mission_fuel_burn_df=mission_fuel_burn_df,
    mission_emissions_kg_df=mission_emissions_summary_df,
    icao_data=icao_data,
    engine_diameter_m=engine_diameter_m,
    engine_cycle_defaults=engine_cycle_defaults,
    engines_per_table=8,
    title_prefix="COMBINED LTO + EMISSIONS + MISSION SUMMARY",
)

# combined_summary_df is returned in case you want to save/export it later.

