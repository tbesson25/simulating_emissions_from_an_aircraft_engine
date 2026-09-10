"""
Main entry point for statistical analysis of model results.

This script evaluates the agreement between model predictions
and reference data using the selected statistical metrics.
"""

"""Final single-workflow script for BPR-grouped fuel-burn and emissions summaries.

This script keeps ONE final printed view grouped by BPR, containing:
- metadata rows
- LTO fuel-burn percent difference rows
- LTO emissions percent difference rows
- LTO emissions absolute kg rows
- mission fuel-burn absolute kg rows
- mission emissions absolute kg rows

Assumptions
-----------
Already have these available in project:
- define_all_engines, build_engines_config, ICAO_fuel_flow
- define_engine
- operating_points, simulate_operating_points
- run_cycle
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

Important
---------
All printed results are grouped by BPR. This is the ONLY final printed table.
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


# ============================================================
# LTO DESIGN / AREA / LTO RESULTS
# ============================================================
from operating_points import operating_points
from operating_points_simulation import simulate_operating_points
from cycle import run_cumpsty_cycle
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
    successful_results = {}
    failed_engines = {}
    for name, data in engines_dict.items():
        engine = data["engine"]
        design_thrust = engine["design_thrust"]
        try:
            results = simulate_operating_points(
                operating_points=operating_points,
                design=design_results_local[name],
                engine=engine,
                areas=area_results_local[name],
                design_thrust=design_thrust,
            )
            successful_results[name] = results
        except Exception as e:
            failed_engines[name] = str(e)
            print(f"Skipping{name}: {e}")
            continue
        print("\n" + "=" * 60)
        print("LTO SIMULATION SUMMARY")
        print("=" * 60)

        print(f"Successful engines: {len(lto_results_local)}")
        print(f"Skipped engines:    {len(failed_engines)}")

        if failed_engines:
            print("\nSkipped engines:")
            for name, error in failed_engines.items():
                print(f"  - {name}: {error}")
        else:
            print("\nNo engines were skipped.")
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

# combined_summary_df is returned in case want to save/export it later.

# ===============================================
# ============================================================
# PLOTS - VALIDATION AND RESULTS
# ============================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import Ellipse


# ============================================================
# OUTPUT FOLDER
# ============================================================

plot_folder = "plots/test"
os.makedirs(plot_folder, exist_ok=True)


# ============================================================
# ENGINE FAMILY DEFINITIONS
# ============================================================

from engine_family_sub import ENGINE_SUBFAMILIES

ENGINE_FAMILIES = ENGINE_SUBFAMILIES


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_lto_fuel_burns(
    engine_name,
    results,
    operating_points,
):
    """
    Calculate total model and ICAO LTO fuel burn.

    Returns
    -------
    model_total : float
        Modelled LTO fuel burn [kg]

    icao_total : float
        ICAO LTO fuel burn [kg]
    """

    model_total = 0.0
    icao_total = 0.0

    for point_name, point in operating_points.items():

        duration = point["time"]

        model_flow = (
            results[point_name]["fuel_mass_flow"]
        )

        icao_flow = (
            ICAO_fuel_flow[engine_name][point_name]
        )

        model_total += model_flow * duration
        icao_total += icao_flow * duration

    return model_total, icao_total


def calculate_lto_fuel_error(
    engine_name,
    results,
    operating_points,
):
    """
    Calculate total LTO fuel-burn percentage error.
    """

    model_total, icao_total = calculate_lto_fuel_burns(
        engine_name=engine_name,
        results=results,
        operating_points=operating_points,
    )

    if icao_total == 0:
        return np.nan

    return (
        (model_total - icao_total)
        / icao_total
        * 100
    )


def build_lto_fuel_error_dataset():
    """
    Build one clean dataset containing:

        engine
        BPR
        design thrust
        total model fuel
        total ICAO fuel
        percentage error

    for all engines with available ICAO data.
    """

    rows = []

    for name, data in engines.items():

        if name not in LTO_results:
            continue

        if name not in ICAO_fuel_flow:
            continue

        engine = data["engine"]

        model_total, icao_total = (
            calculate_lto_fuel_burns(
                engine_name=name,
                results=LTO_results[name],
                operating_points=operating_points,
            )
        )

        if icao_total == 0:
            continue

        percent_error = (
            (model_total - icao_total)
            / icao_total
            * 100
        )

        rows.append({
            "engine": name,
            "BPR": engine["BPR"],
            "design_thrust": engine["design_thrust"],
            "model_fuel": model_total,
            "icao_fuel": icao_total,
            "error_percent": percent_error,
        })

    return pd.DataFrame(rows)


# ============================================================
# BUILD COMMON DATASET
# ============================================================

lto_error_df = build_lto_fuel_error_dataset()




# ============================================================
# LTO FUEL-BURN ERROR STATISTICS BY BPR GROUP
# ============================================================

BPR_BANDS = [
    (4, 6, "BPR 4–6"),
    (6, 8, "BPR 6–8"),
    (8, 10, "BPR 8–10"),
    (10, 12, "BPR 10–12"),
]

bpr_statistics = []
for bpr_min, bpr_max, group_name in BPR_BANDS:

    group = lto_error_df[
        (lto_error_df["BPR"] >= bpr_min)
        & (lto_error_df["BPR"] < bpr_max)
    ]

    if group.empty:
        continue

    errors = group["error_percent"]

    bpr_statistics.append({

        "BPR group": group_name,

        "N": len(errors),

        "Mean error [%]": errors.mean(),

        "Median error [%]": errors.median(),

        "Minimum error [%]": errors.min(),

        "Maximum error [%]": errors.max(),
    })


bpr_statistics_df = pd.DataFrame(
    bpr_statistics
)

print("\n")
print("=" * 90)
print("LTO FUEL-BURN ERROR STATISTICS BY BPR GROUP")
print("=" * 90)

print(
    bpr_statistics_df.to_string(
        index=False,
        float_format=lambda x: f"{x:+.2f}"
    )
)

# ============================================================
# MEAN ABSOLUTE PERCENTAGE ERROR BY BPR GROUP
# ============================================================

bpr_mape = []

for bpr_min, bpr_max, group_name in BPR_BANDS:

    group = lto_error_df[
        (lto_error_df["BPR"] >= bpr_min)
        & (lto_error_df["BPR"] < bpr_max)
    ]

    if group.empty:
        continue

    mape = (
        group["error_percent"]
        .abs()
        .mean()
    )

    bpr_mape.append({
        "BPR group": group_name,
        "MAPE [%]": mape,
    })


bpr_mape_df = pd.DataFrame(
    bpr_mape
)

print("\n")
print(
    bpr_mape_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

# ============================================================
# CORRELATION BETWEEN DESIGN THRUST AND LTO ERROR
# WITHIN EACH BPR GROUP
# ============================================================

for bpr_min, bpr_max, group_name in BPR_BANDS:

    group = lto_error_df[
        (lto_error_df["BPR"] >= bpr_min)
        & (lto_error_df["BPR"] < bpr_max)
    ]

    if len(group) < 3:
        print(
            f"{group_name}: too few engines for correlation"
        )
        continue

    correlation = group[
        "design_thrust"
    ].corr(
        group["error_percent"]
    )

    print(
        f"{group_name}: "
        f"correlation = {correlation:.3f}"
    )

# ============================================================
# LTO EMISSIONS ERROR STATISTICS
# ============================================================

import pandas as pd

emission_statistics = []

species_rows = {
    "NOx": "NOx_%",
    "CO": "CO_%",
    "HC": "HC_%",
}

for species, row_name in species_rows.items():

    if row_name not in LTO_emissions_percent_difference_df.index:
        continue

    errors = (
        LTO_emissions_percent_difference_df
        .loc[row_name]
        .dropna()
    )

    if errors.empty:
        continue

    emission_statistics.append({
        "Pollutant": species,
        "N": len(errors),
        "Mean error [%]": errors.mean(),
        "Median error [%]": errors.median(),
        "MAPE [%]": errors.abs().mean(),
        "Minimum error [%]": errors.min(),
        "Maximum error [%]": errors.max(),
    })


LTO_emissions_error_statistics_df = pd.DataFrame(
    emission_statistics
)


# ============================================================
# PRINT TABLE
# ============================================================

print("\n")
print("=" * 100)
print("LTO EMISSIONS ERROR STATISTICS")
print("=" * 100)

print(
    LTO_emissions_error_statistics_df.to_string(
        index=False,
        formatters={
            "Mean error [%]":
                lambda x: f"{x:+.2f}",
            "Median error [%]":
                lambda x: f"{x:+.2f}",
            "MAPE [%]":
                lambda x: f"{x:.2f}",
            "Minimum error [%]":
                lambda x: f"{x:+.2f}",
            "Maximum error [%]":
                lambda x: f"{x:+.2f}",
        }
    )
)

# ============================================================
# COMPACT LTO EMISSIONS ERROR TABLE
# ============================================================

compact_statistics = []

for species, row_name in species_rows.items():

    if row_name not in LTO_emissions_percent_difference_df.index:
        continue

    errors = (
        LTO_emissions_percent_difference_df
        .loc[row_name]
        .dropna()
    )

    compact_statistics.append({
        "Pollutant": species,
        "N": len(errors),
        "Mean error [%]": errors.mean(),
        "MAPE [%]": errors.abs().mean(),
        "Range [%]": (
            f"{errors.min():+.2f} to "
            f"{errors.max():+.2f}"
        ),
    })


compact_LTO_emissions_statistics_df = pd.DataFrame(
    compact_statistics
)

print("\n")
print("=" * 90)
print("COMPACT LTO EMISSIONS ERROR STATISTICS")
print("=" * 90)

print(
    compact_LTO_emissions_statistics_df.to_string(
        index=False,
        formatters={
            "Mean error [%]":
                lambda x: f"{x:+.2f}",
            "MAPE [%]":
                lambda x: f"{x:.2f}",
        }
    )
)
####NEW1ST
# ============================================================
# LTO FUEL BURN BY PHASE AND BPR GROUP
# ============================================================

# LTO operating-point durations [s]
LTO_DURATIONS = {
    "takeoff": 42.0,
    "climbout": 132.0,
    "approach": 240.0,
    "idle": 1560.0,
}

# Storage
LTO_fuel_burn_by_BPR = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    # --------------------------------------------------------
    # Select engines belonging to the BPR group
    # --------------------------------------------------------
    for name, data in engines.items():

        if name not in mission_results:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    # --------------------------------------------------------
    # Calculate fuel burn for every engine and phase
    # --------------------------------------------------------
    phase_values = {
        "Take-off": [],
        "Climb-out": [],
        "Approach": [],
        "Idle": [],
    }

    for name in selected_engines:

        lto_results = mission_results[name]["lto_results"]

        for phase, label in [
            ("takeoff", "Take-off"),
            ("climbout", "Climb-out"),
            ("approach", "Approach"),
            ("idle", "Idle"),
        ]:

            result = lto_results[phase]

            # Fuel mass flow [kg/s]
            fuel_mass_flow = (
                result["f"]
                * result["mass_flow_core_A4"]
            )

            # Fuel burn during phase [kg]
            fuel_burn = (
                fuel_mass_flow
                * LTO_DURATIONS[phase]
            )

            phase_values[label].append(fuel_burn)

    # --------------------------------------------------------
    # Average fuel burn for the BPR group
    # --------------------------------------------------------
    LTO_fuel_burn_by_BPR[group_name] = {

        phase: np.mean(values) if values else np.nan

        for phase, values in phase_values.items()
    }

    # Total LTO fuel burn
    LTO_fuel_burn_by_BPR[group_name]["LTO total"] = np.sum([
        LTO_fuel_burn_by_BPR[group_name][phase]
        for phase in [
            "Take-off",
            "Climb-out",
            "Approach",
            "Idle",
        ]
    ])


# ============================================================
# PRINT RESULTS
# ============================================================

print("\nAVERAGE LTO FUEL BURN BY BPR GROUP [kg]")
print("-" * 75)

for group, values in LTO_fuel_burn_by_BPR.items():

    print(f"\n{group}")

    for phase, value in values.items():
        print(f"{phase:12s}: {value:10.2f} kg")

# ============================================================
# CHECK AGAINST EXISTING LTO FUEL BURN
# ============================================================

for name in list(mission_results.keys())[:5]:

    lto = mission_results[name]["lto_results"]

    calculated_total = 0.0

    for phase, duration in LTO_DURATIONS.items():

        result = lto[phase]

        fuel_mass_flow = (
            result["f"]
            * result["mass_flow_core_A4"]
        )

        calculated_total += fuel_mass_flow * duration

    existing_total = mission_results[name]["lto_fuel_burn_kg"]

    print(
        name,
        "calculated =", calculated_total,
        "existing =", existing_total,
        "difference =", calculated_total - existing_total
    )


# ============================================================
# LTO EMISSIONS BY BPR GROUP
# ============================================================

lto_emissions_by_BPR = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in LTO_total_emissions_df.columns:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    # --------------------------------------------------------
    # Extract pollutant values
    # --------------------------------------------------------

    NOx_values = [
        LTO_total_emissions_df.loc["NOx_kg", name]
        for name in selected_engines
    ]

    CO_values = [
        LTO_total_emissions_df.loc["CO_kg", name]
        for name in selected_engines
    ]

    HC_values = [
        LTO_total_emissions_df.loc["HC_kg", name]
        for name in selected_engines
    ]

    # --------------------------------------------------------
    # Store statistics
    # --------------------------------------------------------

    lto_emissions_by_BPR[group_name] = {

        "N": len(selected_engines),

        "NOx_mean": np.mean(NOx_values),
        "NOx_median": np.median(NOx_values),
        "NOx_IQR": (
            np.percentile(NOx_values, 75)
            - np.percentile(NOx_values, 25)
        ),

        "CO_mean": np.mean(CO_values),
        "CO_median": np.median(CO_values),
        "CO_IQR": (
            np.percentile(CO_values, 75)
            - np.percentile(CO_values, 25)
        ),

        "HC_mean": np.mean(HC_values),
        "HC_median": np.median(HC_values),
        "HC_IQR": (
            np.percentile(HC_values, 75)
            - np.percentile(HC_values, 25)
        ),
    }


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n============================================")
print("TOTAL LTO EMISSIONS BY BPR GROUP")
print("============================================")

for group, values in lto_emissions_by_BPR.items():

    print(f"\n{group} (N = {values['N']})")

    print(
        f"NOx: mean = {values['NOx_mean']:.2f} kg, "
        f"median = {values['NOx_median']:.2f} kg, "
        f"IQR = {values['NOx_IQR']:.2f} kg"
    )

    print(
        f"CO:  mean = {values['CO_mean']:.2f} kg, "
        f"median = {values['CO_median']:.2f} kg, "
        f"IQR = {values['CO_IQR']:.2f} kg"
    )

    print(
        f"HC:  mean = {values['HC_mean']:.2f} kg, "
        f"median = {values['HC_median']:.2f} kg, "
        f"IQR = {values['HC_IQR']:.2f} kg"
    )

# ============================================================
# AVERAGE LTO EMISSIONS BY BPR GROUP AND LTO PHASE
# ============================================================

LTO_PHASES = [
    "takeoff",
    "climbout",
    "approach",
    "idle"
]

POLLUTANTS = [
    "NOx",
    "CO",
    "HC"
]

lto_emissions_phase_by_BPR = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in all_mission_emissions:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    # --------------------------------------------------------
    # Initialise group
    # --------------------------------------------------------

    lto_emissions_phase_by_BPR[group_name] = {}

    # --------------------------------------------------------
    # Loop through LTO phases
    # --------------------------------------------------------

    for phase in LTO_PHASES:

        lto_emissions_phase_by_BPR[group_name][phase] = {}

        for pollutant in POLLUTANTS:

            values = []

            for name in selected_engines:

                try:

                    value = (
                        all_mission_emissions[name]
                        ["LTO"]
                        [pollutant]
                        [phase]
                        ["emission_mass"]
                    )

                    values.append(float(value))

                except KeyError:
                    continue

            if values:

                lto_emissions_phase_by_BPR[
                    group_name
                ][phase][pollutant] = np.mean(values)

            else:

                lto_emissions_phase_by_BPR[
                    group_name
                ][phase][pollutant] = np.nan


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("AVERAGE LTO EMISSIONS BY BPR GROUP AND PHASE [kg]")
print("=" * 70)

for group in lto_emissions_phase_by_BPR:

    print(f"\n{group}")

    for phase in LTO_PHASES:

        values = lto_emissions_phase_by_BPR[group][phase]

        print(f"\n  {phase}")

        for pollutant in POLLUTANTS:

            print(
                f"    {pollutant}: "
                f"{values[pollutant]:.3f} kg"
            )
