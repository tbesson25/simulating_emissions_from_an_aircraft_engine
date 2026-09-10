from __future__ import annotations
from fontTools.feaLib.ast import HheaField

import pandas as pd
def safe_filename(name):
    return (
        str(name)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace(":", "_")
    )
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


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# OUTPUT FOLDER
# ============================================================

plot_folder = "plots/!!!PRES"

os.makedirs(
    plot_folder,
    exist_ok=True
)

# ACADEMIC / SCIENTIFIC COLOUR CYCLE
# ============================================================
BLUE = "#2F75B5"        # medium scientific blue
BLACK = "#222222"       # near-black
GREEN = "green"       # medium dark green
RED = "#B23A48"         # dark red

plt.rcParams["axes.prop_cycle"] = plt.cycler(
    color=[
        BLUE,
        BLACK,
        GREEN,
        RED,
    ]
)
# ============================================================
# REPORT FIGURE FORMAT
# ============================================================

TITLE_SIZE = 11
LABEL_SIZE = 15
TICK_SIZE = 15
LEGEND_SIZE = 12

# REPORT FIGURE SIZES
FIG_SINGLE = (8, 4)
FIG_WIDE = (9, 5)
FIG_2X2 = (10, 7)
FIG_3PANELS = (15, 4.5)


LTO_PHASES = [
  "takeoff",
  "climbout",
  "approach",
  "idle",
]


for phase in LTO_PHASES:

  model_values = []
  icao_values = []
  bpr_values = []

  for engine_name, results in LTO_results.items():

      if engine_name not in ICAO_fuel_flow:
          continue

      if phase not in results:
          continue

      if phase not in ICAO_fuel_flow[engine_name]:
          continue

      model_flow = (
          results[phase]["fuel_mass_flow"]
      )

      icao_flow = (
          ICAO_fuel_flow[engine_name][phase]
      )

      bpr = engines[engine_name]["engine"]["BPR"]

      model_values.append(model_flow)
      icao_values.append(icao_flow)
      bpr_values.append(bpr)


  model_values = np.array(model_values)
  icao_values = np.array(icao_values)


  # --------------------------------------------------------
  # Plot
  # --------------------------------------------------------

  fig, ax = plt.subplots(figsize = FIG_SINGLE)

  # Individual engines
  ax.scatter(
      icao_values,
      model_values,
      s=55,
  )

  # Determine range
  min_value = min(
      np.min(icao_values),
      np.min(model_values),
  )

  max_value = max(
      np.max(icao_values),
      np.max(model_values),
  )

  x_line = np.linspace(
      min_value,
      max_value,
      200,
  )


  # --------------------------------------------------------
  # Perfect agreement
  # --------------------------------------------------------

  ax.plot(
      x_line,
      x_line,
      linestyle="--",
      linewidth=1.5,
      color="black",
      label="0%",
  )


  # --------------------------------------------------------
  # ±10% agreement
  # --------------------------------------------------------

  ax.plot(
      x_line,
      1.10 * x_line,
      linestyle=":",
      linewidth=1,
      color="blue",
      label="±10%",
  )

  ax.plot(
      x_line,
      0.90 * x_line,
      linestyle=":",
      color="blue",
      linewidth=1,
  )


  # --------------------------------------------------------
  # ±20% agreement
  # --------------------------------------------------------

  ax.plot(
      x_line,
      1.20 * x_line,
      linestyle=":",
      linewidth=1,
      color="green",
      label="±20%",
  )

  ax.plot(
      x_line,
      0.80 * x_line,
      linestyle=":",
      linewidth=1,
      color="green",
  )

  # --------------------------------------------------------
  # ±30% agreement
  # --------------------------------------------------------

  ax.plot(
      x_line,
      1.3 * x_line,
      linestyle=":",
      linewidth=1,
      color="red",
      label="±30%",
  )

  ax.plot(
      x_line,
      0.70 * x_line,
      linestyle=":",
      linewidth=1,
      color="red",
  )
  


# --------------------------------------------------------
# Formatting
# --------------------------------------------------------

  ax.set_xlabel(
    "ICAO fuel mass flow [kg/s]",
    fontsize=LABEL_SIZE
  )

  ax.set_ylabel(
    "Model fuel mass flow [kg/s]",
    fontsize=LABEL_SIZE
  )

# Tick labels
  ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
  )

  ax.grid(True, alpha=0.3)

  ax.legend(
    fontsize=LEGEND_SIZE
)

  plt.tight_layout()

  plt.savefig( 
    os.path.join( 
        plot_folder,
        f"model_vs_ICAO_fuel_flow_{phase}.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

  plt.show()
  plt.close()



# OVERALL LTO FUEL BURN:
# MODELLED VS ICAO
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

model_lto_fuel = []
icao_lto_fuel = []
engine_names = []


# ------------------------------------------------------------
# Calculate total LTO fuel burn for each engine
# ------------------------------------------------------------

for engine_name, results in LTO_results.items():

    # Skip engines without ICAO data
    if engine_name not in ICAO_fuel_flow:
        continue

    model_total = 0.0
    icao_total = 0.0

    for point_name, point in operating_points.items():

        duration = point["time"]

        # Model fuel burn
        model_flow = (
            results[point_name]["fuel_mass_flow"]
        )

        model_total += (
            model_flow * duration
        )

        # ICAO fuel burn
        icao_flow = (
            ICAO_fuel_flow[engine_name][point_name]
        )

        icao_total += (
            icao_flow * duration
        )

    model_lto_fuel.append(model_total)
    icao_lto_fuel.append(icao_total)
    engine_names.append(engine_name)


model_lto_fuel = np.array(model_lto_fuel)
icao_lto_fuel = np.array(icao_lto_fuel)


# ============================================================
# REFERENCE LINE RANGE
# ============================================================

min_value = min(
    np.min(icao_lto_fuel),
    np.min(model_lto_fuel)
)

max_value = max(
    np.max(icao_lto_fuel),
    np.max(model_lto_fuel)
)

x_line = np.linspace(
    min_value,
    max_value,
    200
)


# ============================================================
# MODELLED POINTS
# ============================================================

ax.scatter(
    icao_lto_fuel,
    model_lto_fuel,
    s=55,
)


# ============================================================
# PERFECT AGREEMENT
# ============================================================

ax.plot(
    x_line,
    x_line,
    linestyle="--",
    linewidth=1.5,
    color="black",
    label="0%",
)


# ============================================================
# ±10%
# ============================================================

ax.plot(
    x_line,
    1.10 * x_line,
    linestyle=":",
    linewidth=1,
    color="blue",
    label="±10%",
)

ax.plot(
    x_line,
    0.90 * x_line,
    linestyle=":",
    linewidth=1,
    color="blue",
)


# ============================================================
# ±20%
# ============================================================

ax.plot(
    x_line,
    1.20 * x_line,
    linestyle=":",
    linewidth=1,
    color="green",
    label="±20%",
)

ax.plot(
    x_line,
    0.80 * x_line,
    linestyle=":",
    linewidth=1,
    color="green",
)


# ============================================================
# ±30%
# ============================================================

ax.plot(
    x_line,
    1.30 * x_line,
    linestyle=":",
    linewidth=1,
    color="red",
    label="±30%",
)

ax.plot(
    x_line,
    0.70 * x_line,
    linestyle=":",
    linewidth=1,
    color="red",
)


# Axis labels
ax.set_xlabel(
    "ICAO LTO fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Model LTO fuel burn [kg]",
    fontsize=LABEL_SIZE
)

# Tick labels
ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

# Legend
ax.legend(
    fontsize=LEGEND_SIZE
)

# Grid
ax.grid(
    True,
    alpha=0.3
)


# ============================================================
# AXIS SCALING
# ============================================================

#ax.set_aspect("equal",adjustable="box")

ax.set_xlim(
    min_value,
    max_value
)

ax.set_ylim(
    min_value,
    max_value
)


# ============================================================
# SAVE
# ============================================================

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "model_vs_ICAO_total_LTO_fuel_burn.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

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
lto_error_df = build_lto_fuel_error_dataset()


# ============================================================
# LTO FUEL-BURN ERROR VS DESIGN THRUST
# GROUPED BY BPR
# ============================================================

BPR_BANDS = [
    (4, 6, "BPR 4–6"),
    (6, 8, "BPR 6–8"),
    (8, 10, "BPR 8–10"),
    (10, 12, "BPR 10–12"),
]


fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)


# ------------------------------------------------------------
# Plot each BPR group
# ------------------------------------------------------------

for bpr_min, bpr_max, label in BPR_BANDS:

    mask = (
        (lto_error_df["BPR"] >= bpr_min)
        & (lto_error_df["BPR"] < bpr_max)
    )

    group = lto_error_df.loc[mask]

    if group.empty:
        continue

    ax.scatter(
        group["design_thrust"]/1000,
        group["error_percent"],
        s=55,
        label=label,
    )


# ------------------------------------------------------------
# Zero-error reference
# ------------------------------------------------------------
'''
ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5,
)'''


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

ax.set_xlabel(
    "Design thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Total LTO fuel-burn error [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    title="Bypass ratio",
    fontsize=LEGEND_SIZE
)

plt.tight_layout()


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_fuel_burn_error_vs_design_thrust_grouped_BPR.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()



####
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
MISSION_PHASES = [
    "LTO",
    "Climb",
    "Cruise",
    "Descent",
]
# BUILD AVERAGE MISSION FUEL-BURN DATA
# ============================================================

fuel_burn_by_BPR = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        BPR = data["engine"]["BPR"]

        if (
            BPR >= bpr_min
            and BPR < bpr_max
        ):
            selected_engines.append(name)


    # --------------------------------------------------------
    # Calculate average fuel burn
    # --------------------------------------------------------

    if selected_engines:

        average_fuel = {

            "LTO": np.mean([
                mission_results[name][
                    "lto_fuel_burn_kg"
                ]
                for name in selected_engines
            ]),

            "Climb": np.mean([
                mission_results[name][
                    "climb_fuel_burn_kg"
                ]
                for name in selected_engines
            ]),

            "Cruise": np.mean([
                mission_results[name][
                    "cruise_fuel_burn_kg"
                ]
                for name in selected_engines
            ]),

            "Descent": np.mean([
                mission_results[name][
                    "descent_fuel_burn_kg"
                ]
                for name in selected_engines
            ]),
        }

    else:

        average_fuel = {
            phase: np.nan
            for phase in MISSION_PHASES
        }


    fuel_burn_by_BPR[group_name] = average_fuel


# ============================================================
# AVERAGE TOTAL MISSION FUEL BURN BY BPR GROUP
# ============================================================

average_total_mission_fuel = {}
bpr_labels = []

for bpr_min, bpr_max, group_name in BPR_BANDS:

    if group_name not in fuel_burn_by_BPR:
        continue

    values = fuel_burn_by_BPR[group_name]

    total_fuel = (
        values["LTO"]
        + values["Climb"]
        + values["Cruise"]
        + values["Descent"]
    )

    average_total_mission_fuel[group_name] = total_fuel
    bpr_labels.append(group_name)


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

x = np.arange(
    len(bpr_labels)
)

y = [
    average_total_mission_fuel[group]
    for group in bpr_labels
]

ax.bar(
    x,
    y,
)


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

ax.set_xlabel(
    "Bypass-ratio group",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Average mission fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    bpr_labels,
    fontsize=TICK_SIZE
)

ax.tick_params(
    axis="y",
    labelsize=TICK_SIZE
)

ax.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

plt.savefig(
    os.path.join(
        plot_folder,
        "average_mission_fuel_burn_by_BPR.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()

# ============================================================
# AVERAGE MISSION FUEL BURN BY BPR GROUP
# 2 × 2 PHASE PLOT
# ============================================================

phase_keys = [
    ("LTO", "LTO"),
    ("Climb", "Climb"),
    ("Cruise", "Cruise"),
    ("Descent", "Descent"),
]


fig, axes = plt.subplots(
    2,
    2,
    figsize=(11, 9)
)

axes = axes.flatten()


bpr_labels = [
    group_name
    for bpr_min, bpr_max, group_name in BPR_BANDS
    if group_name in fuel_burn_by_BPR
]


x = np.arange(
    len(bpr_labels)
)


# ------------------------------------------------------------
# Plot each phase
# ------------------------------------------------------------

for ax, (phase_key, phase_title) in zip(
    axes,
    phase_keys
):

    values = [
        fuel_burn_by_BPR[group][phase_key]
        for group in bpr_labels
    ]

    ax.bar(
        x,
        values,
    )

    ax.set_title(
        phase_title,
        fontsize=TITLE_SIZE
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        bpr_labels,
        fontsize=TICK_SIZE
    )

    ax.tick_params(
        axis="y",
        labelsize=TICK_SIZE
    )

    ax.grid(
        axis="y",
        alpha=0.3
    )


# ------------------------------------------------------------
# Common axis labels
# ------------------------------------------------------------

axes[2].set_xlabel(
    "Bypass-ratio group",
    fontsize=LABEL_SIZE
)

axes[3].set_xlabel(
    "Bypass-ratio group",
    fontsize=LABEL_SIZE
)

axes[0].set_ylabel(
    "Average fuel burn [kg]",
    fontsize=LABEL_SIZE
)

axes[2].set_ylabel(
    "Average fuel burn [kg]",
    fontsize=LABEL_SIZE
)


plt.tight_layout()


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

plt.savefig(
    os.path.join(
        plot_folder,
        "average_mission_fuel_burn_by_BPR_2x2.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()

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
# 3. AVERAGE EMISSIONS: 2x2 BY BPR GROUP
# ============================================================
#
# This version shows:
#
#    x = flight phase
#    y = average pollutant mass
#    NOx/CO/HC = stacked
#
# One panel per BPR group.
# ============================================================
# BUILD AVERAGE MISSION EMISSIONS BY BPR GROUP
# ============================================================

emissions_by_BPR = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        if name not in mission_emissions_summary_df.columns:
            continue

        BPR = data["engine"]["BPR"]

        if (
            BPR >= bpr_min
            and BPR < bpr_max
        ):
            selected_engines.append(name)


    # --------------------------------------------------------
    # Average emissions
    # --------------------------------------------------------

    average_emissions = {}

    for phase in MISSION_PHASES:

        if selected_engines:

            phase_key = phase.upper()

            # LTO
            if phase == "LTO":
                NOx_row = "LTO_NOx_kg"
                CO_row = "LTO_CO_kg"
                HC_row = "LTO_HC_kg"

            # Climb
            elif phase == "Climb":
                NOx_row = "CLIMB_NOx_kg"
                CO_row = "CLIMB_CO_kg"
                HC_row = "CLIMB_HC_kg"

            # Cruise
            elif phase == "Cruise":
                NOx_row = "CRUISE_NOx_kg"
                CO_row = "CRUISE_CO_kg"
                HC_row = "CRUISE_HC_kg"

            # Descent
            elif phase == "Descent":
                NOx_row = "DESCENT_NOx_kg"
                CO_row = "DESCENT_CO_kg"
                HC_row = "DESCENT_HC_kg"

            average_emissions[phase] = {

                "NOx": np.mean([
                    mission_emissions_summary_df.loc[
                        NOx_row,
                        name
                    ]
                    for name in selected_engines
                ]),

                "CO": np.mean([
                    mission_emissions_summary_df.loc[
                        CO_row,
                        name
                    ]
                    for name in selected_engines
                ]),

                "HC": np.mean([
                    mission_emissions_summary_df.loc[
                        HC_row,
                        name
                    ]
                    for name in selected_engines
                ]),
            }

        else:

            average_emissions[phase] = {
                "NOx": np.nan,
                "CO": np.nan,
                "HC": np.nan,
            }


    emissions_by_BPR[group_name] = (
        average_emissions
    )

fig, axes = plt.subplots(
    2,
    2,
    figsize=(11, 9),
)

axes = axes.flatten()


for ax, (
    bpr_min,
    bpr_max,
    group_name,
) in zip(
    axes,
    BPR_BANDS,
):

    # --------------------------------------------------------
    # Extract average values already calculated above
    # --------------------------------------------------------

    NOx_values = np.array([
        emissions_by_BPR[group_name][phase]["NOx"]
        for phase in MISSION_PHASES
    ])

    CO_values = np.array([
        emissions_by_BPR[group_name][phase]["CO"]
        for phase in MISSION_PHASES
    ])

    HC_values = np.array([
        emissions_by_BPR[group_name][phase]["HC"]
        for phase in MISSION_PHASES
    ])


    x = np.arange(
        len(MISSION_PHASES)
    )


    # --------------------------------------------------------
    # Stacked bars
    # --------------------------------------------------------

    ax.bar(
        x,
        NOx_values,
        label="NOx",
    )

    ax.bar(
        x,
        CO_values,
        bottom=NOx_values,
        label="CO",
    )

    ax.bar(
        x,
        HC_values,
        bottom=NOx_values + CO_values,
        label="HC",
    )


    # --------------------------------------------------------
    # Formatting
    # --------------------------------------------------------

    ax.set_title(
        group_name,
        fontsize=TITLE_SIZE,
    )

    ax.set_xticks(x)

    ax.set_xticklabels(
        MISSION_PHASES,
        fontsize=TICK_SIZE,
    )

    ax.tick_params(
        axis="y",
        labelsize=TICK_SIZE,
    )

    ax.grid(
        True,
        axis="y",
        alpha=0.3,
    )


# ============================================================
# COMMON AXIS LABELS
# ============================================================

axes[0].set_ylabel(
    "Average emissions [kg]",
    fontsize=LABEL_SIZE,
)

axes[2].set_ylabel(
    "Average emissions [kg]",
    fontsize=LABEL_SIZE,
)

# COMMON X-AXIS LABELS
# ============================================================

axes[2].set_xlabel(
    "Mission phase",
    fontsize=LABEL_SIZE,
)

axes[3].set_xlabel(
    "Mission phase",
    fontsize=LABEL_SIZE,
)


# ============================================================
# COMMON LEGEND
# ============================================================

handles, labels = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    labels,
    loc="upper center",
    ncol=3,
    fontsize=LEGEND_SIZE,
    bbox_to_anchor=(0.5, 0.99),
)

plt.tight_layout(
    rect=[0, 0, 1, 0.93]
)

plt.savefig(
    os.path.join(
        plot_folder,
        "average_mission_emissions_by_BPR_2x2.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()

# ============================================================
# AVERAGE MISSION EMISSIONS BY BPR GROUP
# SEPARATE FIGURES
# ============================================================

for bpr_min, bpr_max, group_name in BPR_BANDS:

    # --------------------------------------------------------
    # Extract average values already calculated above
    # --------------------------------------------------------

    NOx_values = np.array([
        emissions_by_BPR[group_name][phase]["NOx"]
        for phase in MISSION_PHASES
    ])

    CO_values = np.array([
        emissions_by_BPR[group_name][phase]["CO"]
        for phase in MISSION_PHASES
    ])

    HC_values = np.array([
        emissions_by_BPR[group_name][phase]["HC"]
        for phase in MISSION_PHASES
    ])

    x = np.arange(
        len(MISSION_PHASES)
    )


    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize = FIG_SINGLE
    )

    ax.bar(
        x,
        NOx_values,
        label="NO$_x$",
        color=BLUE,
    )

    ax.bar(
        x,
        CO_values,
        bottom=NOx_values,
        label="CO",
        color=BLACK,
    )

    ax.bar(
        x,
        HC_values,
        bottom=NOx_values + CO_values,
        label="HC",
        color=GREEN,
    )


    # --------------------------------------------------------
    # Formatting
    # --------------------------------------------------------

    ax.set_xlabel(
        "Mission phase",
        fontsize=LABEL_SIZE
    )

    ax.set_ylabel(
        "Average emissions [kg]",
        fontsize=LABEL_SIZE
    )

    ax.set_xticks(
        x
    )

    ax.set_xticklabels(
        MISSION_PHASES,
        fontsize=TICK_SIZE
    )

    ax.tick_params(
        axis="y",
        labelsize=TICK_SIZE
    )

    ax.grid(
        True,
        axis="y",
        alpha=0.3,
    )

    ax.legend(
        fontsize=LEGEND_SIZE
    )


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    filename = (
        group_name
        .replace(" ", "_")
        .replace("–", "-")
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            plot_folder,
            f"average_mission_emissions_{filename}.png",
        ),
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()
    plt.close()

# ============================================================
# DESIGN-POINT TSFC VS BPR
# ============================================================

bpr_values = []
tsfc_values = []

for name, data in engines.items():

    if name not in design_results:
        continue

    engine = data["engine"]

    BPR = engine["BPR"]

    results = design_results[name]

    # Change this key if your design-results dictionary
    # uses a different name for TSFC.
    TSFC = results["TSFC"]

    if not np.isfinite(BPR):
        continue

    if not np.isfinite(TSFC):
        continue

    bpr_values.append(BPR)
    tsfc_values.append(TSFC)


bpr_values = np.array(bpr_values)
tsfc_values = np.array(tsfc_values)


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

ax.scatter(
    bpr_values,
    tsfc_values,
    s=55,
)


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "TSFC [kg/(N·s)]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    os.path.join(
        plot_folder,
        "design_TSFC_vs_BPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# DESIGN-POINT EFFICIENCIES VS BPR
# ============================================================

bpr_values = []

eta_th_values = []
eta_p_values = []
eta_o_values = []

for name, data in engines.items():

    if name not in design_results:
        continue

    BPR = data["engine"]["BPR"]
    results = design_results[name]

    eta_th = results["eta_thermal"]
    eta_p = results["eta_propulsive"]
    eta_o = results["eta_overall"]

    if not all(
        np.isfinite(value)
        for value in [BPR, eta_th, eta_p, eta_o]
    ):
        continue

    bpr_values.append(BPR)
    eta_th_values.append(eta_th * 100)
    eta_p_values.append(eta_p * 100)
    eta_o_values.append(eta_o * 100)


bpr_values = np.array(bpr_values)
eta_th_values = np.array(eta_th_values)
eta_p_values = np.array(eta_p_values)
eta_o_values = np.array(eta_o_values)


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

ax.scatter(
    bpr_values,
    eta_th_values,
    s=55,
    color=BLUE,
    label=r"$\eta_{th}$",
)

ax.scatter(
    bpr_values,
    eta_p_values,
    s=55,
    marker="s",
    color=BLACK,
    label=r"$\eta_p$",
)

ax.scatter(
    bpr_values,
    eta_o_values,
    s=55,
    marker="^",
    color=GREEN,
    label=r"$\eta_o$",
)


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Efficiency [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    fontsize=LEGEND_SIZE
)

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    os.path.join(
        plot_folder,
        "design_efficiency_vs_BPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# FUEL MASS FLOW, FPR AND BPR VS T04
# LTO OPERATING POINTS
# ============================================================

for phase in LTO_PHASES:

    T04_values = []
    fuel_flow_values = []
    FPR_values = []
    BPR_values = []

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        if phase not in results:
            continue

        point = results[phase]

        T04 = point["T04"]
        fuel_flow = point["fuel_mass_flow"]
        FPR = point["FPR"]
        BPR = point["BPR"]

        if not all(
            np.isfinite(value)
            for value in [T04, fuel_flow, FPR, BPR]
        ):
            continue

        T04_values.append(T04)
        fuel_flow_values.append(fuel_flow)
        FPR_values.append(FPR)
        BPR_values.append(BPR)


    T04_values = np.array(T04_values)
    fuel_flow_values = np.array(fuel_flow_values)
    FPR_values = np.array(FPR_values)
    BPR_values = np.array(BPR_values)


    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    fig, ax1 = plt.subplots(
        figsize = FIG_SINGLE
    )

    # Fuel mass flow
    ax1.scatter(
        T04_values,
        fuel_flow_values,
        s=55,
        marker="o",
        color=BLUE,
        label=r"$\dot{m}_f$",
    )


    ax1.set_xlabel(
        r"$T_{04}$ [K]",
        fontsize=LABEL_SIZE
    )

    ax1.set_ylabel(
        r"Fuel mass flow [kg/s]",
        fontsize=LABEL_SIZE
    )

    ax1.tick_params(
        axis="both",
        labelsize=TICK_SIZE
    )

    ax1.grid(
        True,
        alpha=0.3
    )


    # --------------------------------------------------------
    # Secondary axis
    # --------------------------------------------------------

    ax2 = ax1.twinx()

    ax2.scatter(
        T04_values,
        FPR_values,
        s=55,
        marker="s",
        color=GREEN,
        label="FPR",
    )

    ax2.scatter(
        T04_values,
        BPR_values,
        s=55,
        marker="^",
        color=RED,
        label="BPR",
    )

    ax2.set_ylabel(
        "FPR / BPR",
        fontsize=LABEL_SIZE
    )

    ax2.tick_params(
        axis="y",
        labelsize=TICK_SIZE
    )


    # --------------------------------------------------------
    # Combined legend
    # --------------------------------------------------------

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        fontsize=LEGEND_SIZE
    )


    plt.tight_layout()


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    plt.savefig(
        os.path.join(
            plot_folder,
            f"fuel_flow_FPR_BPR_vs_T04_{phase}.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

# ============================================================
# FUEL MASS FLOW, FPR AND BPR VS T04
# DESIGN-POINT / CRUISE
# ============================================================

T04_values = []
fuel_flow_values = []
FPR_values = []
BPR_values = []


for name, results in design_results.items():

    if name not in engines:
        continue

    T04 = results["T04"]
    fuel_flow = results["fuel_mass_flow"]
    
    if not all(
        np.isfinite(value)
        for value in [T04, fuel_flow]
    ):
        continue

    T04_values.append(T04)
    fuel_flow_values.append(fuel_flow)



T04_values = np.array(T04_values)
fuel_flow_values = np.array(fuel_flow_values)

# ============================================================
# PLOT
# ============================================================

fig, ax1 = plt.subplots(
    figsize = FIG_SINGLE
)

# Fuel mass flow
ax1.scatter(
    T04_values,
    fuel_flow_values,
    s=55,
    label=r"$\dot{m}_f$",
)

ax1.set_xlabel(
    r"$T_{04}$ [K]",
    fontsize=LABEL_SIZE
)

ax1.set_ylabel(
    "Fuel mass flow [kg/s]",
    fontsize=LABEL_SIZE
)

ax1.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax1.grid(
    True,
    alpha=0.3
)


# ============================================================
# SECONDARY AXIS
# ============================================================

ax2 = ax1.twinx()


ax2.tick_params(
    axis="y",
    labelsize=TICK_SIZE
)


# ============================================================
# LEGEND
# ============================================================

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    handles1 + handles2,
    labels1 + labels2,
    fontsize=LEGEND_SIZE
)


plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    os.path.join(
        plot_folder,
        "fuel_flow_FPR_BPR_vs_T04_cruisechanged.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# OFF-DESIGN PARAMETERS VS THRUST LEVEL
# 2 x 2 FIGURE
# ============================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(11, 9)
)

axes = axes.flatten()


# ------------------------------------------------------------
# Plot definitions
# ------------------------------------------------------------

plot_definitions = [
    (
        "T04",
        r"$T_{04}$ [K]",
        "$T_{04}$",
    ),
    (
        "CPR",
        "Compressor pressure ratio",
        "CPR",
    ),
    (
        "BPR",
        "Bypass ratio",
        "BPR",
    ),
    (
        "fuel_mass_flow",
        "Fuel mass flow [kg/s]",
        r"$\dot{m}_f$",
    ),
]


# ------------------------------------------------------------
# Build data
# ------------------------------------------------------------

for ax, (
    parameter_key,
    ylabel,
    label,
) in zip(
    axes,
    plot_definitions,
):

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        thrust_values = []
        parameter_values = []

        design_thrust = (
            engines[name]["engine"]["design_thrust"]
        )

        for phase in LTO_PHASES:

            if phase not in results:
                continue

            point = results[phase]

            # ------------------------------------------------
            # Actual thrust represented by the operating point
            # ------------------------------------------------

            thrust_level = (
                operating_points[phase]["thrust_level"]
            )

            thrust = (
                thrust_level * design_thrust
            )

            # ------------------------------------------------
            # Parameter
            # ------------------------------------------------

            if parameter_key not in point:
                continue

            value = point[parameter_key]

            if not np.isfinite(value):
                continue

            if not np.isfinite(thrust):
                continue

            thrust_values.append(thrust)
            parameter_values.append(value)

        if not thrust_values:
            continue

        ax.plot(
            thrust_values,
            parameter_values,
            marker="o",
            markersize=4,
            linewidth=0.8,
            alpha=0.45,
        )


    # --------------------------------------------------------
    # Formatting
    # --------------------------------------------------------

    ax.set_xlabel(
        "Thrust [N]",
        fontsize=LABEL_SIZE
    )

    ax.set_ylabel(
        ylabel,
        fontsize=LABEL_SIZE
    )

    ax.tick_params(
        axis="both",
        labelsize=TICK_SIZE
    )

    ax.grid(
        True,
        alpha=0.3
    )

    ax.set_title(
        label,
        fontsize=TITLE_SIZE
    )


plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_parameters_vs_thrust_level_2x2.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# REPRESENTATIVE ENGINE FOR OFF-DESIGN BEHAVIOUR PLOTS
# ============================================================

REPRESENTATIVE_ENGINE = "CFM56-5B1/3"
results = LTO_results[REPRESENTATIVE_ENGINE]

# ============================================================
# REPRESENTATIVE ENGINE
# ============================================================

engine_name = REPRESENTATIVE_ENGINE

results = LTO_results[engine_name]


T04_values = []
fuel_flow_values = []
FPR_values = []
BPR_values = []


for phase in LTO_PHASES:

    if phase not in results:
        continue

    point = results[phase]

    T04_values.append(
        point["T04"]
    )

    fuel_flow_values.append(
        point["fuel_mass_flow"]
    )

    FPR_values.append(
        point["FPR"]
    )

    BPR_values.append(
        point["BPR"]
    )


T04_values = np.array(T04_values)
fuel_flow_values = np.array(fuel_flow_values)
FPR_values = np.array(FPR_values)
BPR_values = np.array(BPR_values)


# ============================================================
# PLOT
# ============================================================

fig, ax1 = plt.subplots(
    figsize = FIG_SINGLE
)

ax1.scatter(
    T04_values,
    fuel_flow_values,
    s=55,
    label=r"$\dot{m}_f$",
)

ax1.set_xlabel(
    r"$T_{04}$ [K]",
    fontsize=LABEL_SIZE
)

ax1.set_ylabel(
    "Fuel mass flow [kg/s]",
    fontsize=LABEL_SIZE
)

ax1.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax1.grid(
    True,
    alpha=0.3
)


ax2 = ax1.twinx()

ax2.scatter(
    T04_values,
    FPR_values,
    s=55,
    marker="s",
    label="FPR",
)

ax2.scatter(
    T04_values,
    BPR_values,
    s=55,
    marker="^",
    label="BPR",
)

ax2.set_ylabel(
    "FPR / BPR",
    fontsize=LABEL_SIZE
)

ax2.tick_params(
    axis="y",
    labelsize=TICK_SIZE
)


handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(
    handles1 + handles2,
    labels1 + labels2,
    fontsize=LEGEND_SIZE
)


plt.tight_layout()


safe_name = safe_filename(engine_name)
plt.savefig(
    os.path.join(
        plot_folder,
        f"{safe_name}_fuel_flow_FPR_BPR_vs_T04_LTO.png"
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()


# ============================================================
# OFF-DESIGN ENGINE-BEHAVIOUR PLOTS
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# BPR colour scale
BPR_MIN = 4
BPR_MAX = 12

norm = mpl.colors.Normalize(
    vmin=BPR_MIN,
    vmax=BPR_MAX
)

cmap = mpl.colormaps["viridis_r"]

# ============================================================
# T04 VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    T04_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        # Convert thrust to kN
        thrust = (
            thrust_level
            * design_thrust
            / 1000
        )

        T04 = point["T04"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(T04):
            continue

        thrust_values.append(thrust)
        T04_values.append(T04)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    T04_values = np.array(T04_values)[order]

    ax.plot(
        thrust_values,
        T04_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    r"$T_{04}$ [K]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


# ============================================================
# BPR COLOURBAR
# ============================================================

sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_T04_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# CPR VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    CPR_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = (
            thrust_level
            * design_thrust
            / 1000
        )

        CPR = point["CPR"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(CPR):
            continue

        thrust_values.append(thrust)
        CPR_values.append(CPR)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    CPR_values = np.array(CPR_values)[order]

    ax.plot(
        thrust_values,
        CPR_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Compressor pressure ratio, CPR",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_CPR_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# FPR VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    FPR_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = (
            thrust_level
            * design_thrust
            / 1000
        )

        FPR = point["FPR"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(FPR):
            continue

        thrust_values.append(thrust)
        FPR_values.append(FPR)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    FPR_values = np.array(FPR_values)[order]

    ax.plot(
        thrust_values,
        FPR_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Fan pressure ratio, FPR",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_FPR_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# BPR VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR_colour = engine["BPR"]

    thrust_values = []
    BPR_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = (
            thrust_level
            * design_thrust
            / 1000
        )

        BPR = point["BPR"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(BPR):
            continue

        thrust_values.append(thrust)
        BPR_values.append(BPR)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    BPR_values = np.array(BPR_values)[order]

    ax.plot(
        thrust_values,
        BPR_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR_colour)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Design-point BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_BPR_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# FUEL MASS FLOW VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    fuel_flow_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = (
            thrust_level
            * design_thrust
            / 1000
        )

        fuel_flow = point["fuel_mass_flow"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(fuel_flow):
            continue

        thrust_values.append(thrust)
        fuel_flow_values.append(fuel_flow)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    fuel_flow_values = np.array(fuel_flow_values)[order]

    ax.plot(
        thrust_values,
        fuel_flow_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Fuel mass flow [kg/s]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_fuel_mass_flow_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# EFFICIENCIES VS THRUST
# ============================================================

fig, axes = plt.subplots(
    1,
    3,
    figsize=(16, 5)
)

efficiency_definitions = [
    ("n_th", r"$\eta_{th}$", "Thermal efficiency [%]"),
    ("n_p", r"$\eta_p$", "Propulsive efficiency [%]"),
    ("n_o", r"$\eta_o$", "Overall efficiency [%]"),
]


for ax, (parameter_key, title, ylabel) in zip(
    axes,
    efficiency_definitions
):

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        engine = engines[name]["engine"]

        design_thrust = engine["design_thrust"]
        BPR = engine["BPR"]

        thrust_values = []
        efficiency_values = []

        for phase in LTO_PHASES:

            if phase not in results:
                continue

            if phase not in operating_points:
                continue

            point = results[phase]

            thrust_level = (
                operating_points[phase]["thrust_level"]
            )

            thrust = (
                thrust_level
                * design_thrust
                / 1000
            )

            if parameter_key not in point:
                continue

            efficiency = point[parameter_key]

            if not np.isfinite(thrust):
                continue

            if not np.isfinite(efficiency):
                continue

            thrust_values.append(thrust)

            efficiency_values.append(
                efficiency * 100
            )

        if not thrust_values:
            continue

        order = np.argsort(thrust_values)

        thrust_values = np.array(thrust_values)[order]
        efficiency_values = np.array(
            efficiency_values
        )[order]

        ax.plot(
            thrust_values,
            efficiency_values,
            marker="o",
            markersize=3.5,
            linewidth=1.0,
            alpha=0.55,
            color=cmap(norm(BPR)),
        )


    ax.set_xlabel(
        "Thrust [kN]",
        fontsize=LABEL_SIZE
    )

    ax.set_ylabel(
        ylabel,
        fontsize=LABEL_SIZE
    )

    ax.set_title(
        title,
        fontsize=TITLE_SIZE
    )

    ax.tick_params(
        axis="both",
        labelsize=TICK_SIZE
    )

    ax.grid(
        True,
        alpha=0.3
    )


# ============================================================
# COMMON BPR COLOURBAR
# ============================================================

sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=axes,
    shrink=0.9
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_efficiencies_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# THERMAL EFFICIENCY VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    efficiency_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = thrust_level * design_thrust / 1000

        efficiency = point["n_th"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(efficiency):
            continue

        thrust_values.append(thrust)
        efficiency_values.append(efficiency * 100)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    efficiency_values = np.array(efficiency_values)[order]

    ax.plot(
        thrust_values,
        efficiency_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    r"Thermal efficiency, $\eta_{th}$ [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_thermal_efficiency_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# PROPULSIVE EFFICIENCY VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    efficiency_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = thrust_level * design_thrust / 1000

        efficiency = point["n_p"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(efficiency):
            continue

        thrust_values.append(thrust)
        efficiency_values.append(efficiency * 100)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    efficiency_values = np.array(efficiency_values)[order]

    ax.plot(
        thrust_values,
        efficiency_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    r"Propulsive efficiency, $\eta_p$ [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_propulsive_efficiency_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# OVERALL EFFICIENCY VS THRUST
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

for name, results in LTO_results.items():

    if name not in engines:
        continue

    engine = engines[name]["engine"]

    design_thrust = engine["design_thrust"]
    BPR = engine["BPR"]

    thrust_values = []
    efficiency_values = []

    for phase in LTO_PHASES:

        if phase not in results:
            continue

        point = results[phase]

        thrust_level = operating_points[phase]["thrust_level"]

        thrust = thrust_level * design_thrust / 1000

        efficiency = point["n_o"]

        if not np.isfinite(thrust):
            continue

        if not np.isfinite(efficiency):
            continue

        thrust_values.append(thrust)
        efficiency_values.append(efficiency * 100)

    if not thrust_values:
        continue

    order = np.argsort(thrust_values)

    thrust_values = np.array(thrust_values)[order]
    efficiency_values = np.array(efficiency_values)[order]

    ax.plot(
        thrust_values,
        efficiency_values,
        marker="o",
        markersize=4,
        linewidth=1.2,
        alpha=0.65,
        color=cmap(norm(BPR)),
    )


ax.set_xlabel(
    "Thrust [kN]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    r"Overall efficiency, $\eta_o$ [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)


sm = mpl.cm.ScalarMappable(
    norm=norm,
    cmap=cmap
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=ax
)

cbar.set_label(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

cbar.ax.tick_params(
    labelsize=TICK_SIZE
)


plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "off_design_overall_efficiency_vs_thrust.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# LATEX TABLE: AVERAGE MISSION FUEL BURN BY BPR GROUP
# ============================================================

print(r"\begin{table}[H]")
print(r"\centering")
print(r"\caption{Average mission fuel burn by bypass-ratio group and flight phase.}")
print(r"\label{tab:average_mission_fuel_burn_BPR}")
print(r"\begin{tabular}{lrrrrr}")
print(r"\hline")
print(
    r"\textbf{BPR group} & "
    r"\textbf{LTO} & "
    r"\textbf{Climb} & "
    r"\textbf{Cruise} & "
    r"\textbf{Descent} & "
    r"\textbf{Total} \\"
)
print(r"\hline")

for group_name, values in fuel_burn_by_BPR.items():

    total = (
        values["LTO"]
        + values["Climb"]
        + values["Cruise"]
        + values["Descent"]
    )

    print(
        f"{group_name} & "
        f"{values['LTO']:.1f} & "
        f"{values['Climb']:.1f} & "
        f"{values['Cruise']:.1f} & "
        f"{values['Descent']:.1f} & "
        f"{total:.1f} \\\\"
    )

print(r"\hline")
print(r"\end{tabular}")
print(r"\end{table}")


# ============================================================
# LTO PHASE FUEL-BURN PLOT SETTINGS
# ============================================================

PHASE_COLORS = {
    "takeoff": BLUE,
    "climbout": BLACK,
    "approach": GREEN,
    "idle": RED,
}

PHASE_MARKERS = {
    "takeoff": "o",
    "climbout": "s",
    "approach": "^",
    "idle": "D",
}

# ============================================================
# LTO PHASE FUEL BURN VS T04
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)


for phase in LTO_PHASES:

    T04_values = []
    fuel_burn_values = []

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        T04 = point["T04"]
        fuel_mass_flow = point["fuel_mass_flow"]

        duration = operating_points[phase]["time"]

        fuel_burn = (
            fuel_mass_flow * duration
        )

        if not np.isfinite(T04):
            continue

        if not np.isfinite(fuel_burn):
            continue

        T04_values.append(T04)
        fuel_burn_values.append(fuel_burn)


    ax.scatter(
        T04_values,
        fuel_burn_values,
        s=55,
        marker=PHASE_MARKERS[phase],
        color=PHASE_COLORS[phase],
        label=phase.capitalize(),
    )


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    r"$T_{04}$ [K]",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "LTO phase fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    fontsize=LEGEND_SIZE,
    title="LTO phase",
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_phase_fuel_burn_vs_T04.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# LTO PHASE FUEL BURN VS FPR
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)


for phase in LTO_PHASES:

    FPR_values = []
    fuel_burn_values = []

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        FPR = point["FPR"]
        fuel_mass_flow = point["fuel_mass_flow"]

        duration = operating_points[phase]["time"]

        fuel_burn = (
            fuel_mass_flow * duration
        )

        if not np.isfinite(FPR):
            continue

        if not np.isfinite(fuel_burn):
            continue

        FPR_values.append(FPR)
        fuel_burn_values.append(fuel_burn)


    ax.scatter(
        FPR_values,
        fuel_burn_values,
        s=55,
        marker=PHASE_MARKERS[phase],
        color=PHASE_COLORS[phase],
        label=phase.capitalize(),
    )


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Fan pressure ratio, FPR",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "LTO phase fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    fontsize=LEGEND_SIZE,
    title="LTO phase",
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_phase_fuel_burn_vs_FPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# LTO PHASE FUEL BURN VS BPR
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)


for phase in LTO_PHASES:

    BPR_values = []
    fuel_burn_values = []

    for name, results in LTO_results.items():

        if name not in engines:
            continue

        if phase not in results:
            continue

        if phase not in operating_points:
            continue

        point = results[phase]

        BPR = point["BPR"]
        fuel_mass_flow = point["fuel_mass_flow"]

        duration = operating_points[phase]["time"]

        fuel_burn = (
            fuel_mass_flow * duration
        )

        if not np.isfinite(BPR):
            continue

        if not np.isfinite(fuel_burn):
            continue

        BPR_values.append(BPR)
        fuel_burn_values.append(fuel_burn)


    ax.scatter(
        BPR_values,
        fuel_burn_values,
        s=55,
        marker=PHASE_MARKERS[phase],
        color=PHASE_COLORS[phase],
        label=phase.capitalize(),
    )


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "LTO phase fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    fontsize=LEGEND_SIZE,
    title="LTO phase",
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_phase_fuel_burn_vs_BPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# T04 DISTRIBUTION BY LTO PHASE
# ============================================================

T04_distribution = []

for phase in LTO_PHASES:

    values = []

    for name, results in LTO_results.items():

        if phase not in results:
            continue

        T04 = results[phase]["T04"]

        if np.isfinite(T04):
            values.append(T04)

    T04_distribution.append(values)


fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

bp = ax.boxplot(
    T04_distribution,
    labels=["Take-off", "Climb-out", "Approach", "Idle"],
    patch_artist=False,
    showfliers=True,
)


ax.set_xlabel(
    "LTO operating point",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    r"$T_{04}$ [K]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_T04_distribution_by_phase.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# FPR DISTRIBUTION BY LTO PHASE
# ============================================================

FPR_distribution = []

for phase in LTO_PHASES:

    values = []

    for name, results in LTO_results.items():

        if phase not in results:
            continue

        FPR = results[phase]["FPR"]

        if np.isfinite(FPR):
            values.append(FPR)

    FPR_distribution.append(values)


fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

ax.boxplot(
    FPR_distribution,
    labels=["Take-off", "Climb-out", "Approach", "Idle"],
    patch_artist=False,
    showfliers=True,
)

ax.set_xlabel(
    "LTO operating point",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Fan pressure ratio, FPR",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_FPR_distribution_by_phase.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# BPR DISTRIBUTION BY LTO PHASE
# ============================================================

BPR_distribution = []

for phase in LTO_PHASES:

    values = []

    for name, results in LTO_results.items():

        if phase not in results:
            continue

        BPR = results[phase]["BPR"]

        if np.isfinite(BPR):
            values.append(BPR)

    BPR_distribution.append(values)


fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

ax.boxplot(
    BPR_distribution,
    labels=["Take-off", "Climb-out", "Approach", "Idle"],
    patch_artist=False,
    showfliers=True,
)

ax.set_xlabel(
    "LTO operating point",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Bypass ratio, BPR",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_BPR_distribution_by_phase.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# LTO FUEL-BURN CONTRIBUTION BY PHASE AND BPR GROUP
# ============================================================

fuel_burn_contribution = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in LTO_results:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    if not selected_engines:
        continue


    # --------------------------------------------------------
    # Average phase fuel burn
    # --------------------------------------------------------

    average_phase_fuel = {}

    for phase in LTO_PHASES:

        values = []

        for name in selected_engines:

            if phase not in LTO_results[name]:
                continue

            fuel_flow = (
                LTO_results[name][phase]["fuel_mass_flow"]
            )

            duration = operating_points[phase]["time"]

            values.append(
                fuel_flow * duration
            )

        average_phase_fuel[phase] = np.mean(values)


    total = sum(
        average_phase_fuel[phase]
        for phase in LTO_PHASES
    )


    fuel_burn_contribution[group_name] = {
        phase:
            100
            * average_phase_fuel[phase]
            / total
        for phase in LTO_PHASES
    }


# ============================================================
# PLOT
# ============================================================

fig, ax = plt.subplots(
    figsize = FIG_SINGLE
)

x = np.arange(
    len(fuel_burn_contribution)
)

bottom = np.zeros(
    len(fuel_burn_contribution)
)


PHASE_COLORS = {
    "takeoff": BLACK,
    "climbout": GREEN,
    "approach": RED,
    "idle": BLUE,
}


PHASE_LABELS = {
    "takeoff": "Take-off",
    "climbout": "Climb-out",
    "approach": "Approach",
    "idle": "Idle",
}


for phase in LTO_PHASES:

    values = np.array([
        fuel_burn_contribution[group][phase]
        for group in fuel_burn_contribution
    ])

    ax.bar(
        x,
        values,
        bottom=bottom,
        color=PHASE_COLORS[phase],
        label=PHASE_LABELS[phase],
    )

    bottom += values


# ============================================================
# FORMATTING
# ============================================================

ax.set_xlabel(
    "Bypass-ratio group",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Contribution to total LTO fuel burn [%]",
    fontsize=LABEL_SIZE
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    fuel_burn_contribution.keys(),
    fontsize=TICK_SIZE
)

ax.tick_params(
    axis="y",
    labelsize=TICK_SIZE
)

ax.set_ylim(
    0,
    100
)

ax.grid(
    True,
    axis="y",
    alpha=0.3
)

ax.legend(
    fontsize=LEGEND_SIZE
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_fuel_burn_contribution_by_phase_BPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# ============================================================
# TOTAL MISSION FUEL-BURN STATISTICS BY BPR GROUP
# ============================================================

mission_fuel_statistics = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    if not selected_engines:
        continue

    total_fuel_values = []

    for name in selected_engines:

        result = mission_results[name]

        total_fuel = (
            result["lto_fuel_burn_kg"]
            + result["climb_fuel_burn_kg"]
            + result["cruise_fuel_burn_kg"]
            + result["descent_fuel_burn_kg"]
        )

        if np.isfinite(total_fuel):
            total_fuel_values.append(total_fuel)

    total_fuel_values = np.array(total_fuel_values)

    if len(total_fuel_values) == 0:
        continue

    mission_fuel_statistics[group_name] = {
        "N": len(total_fuel_values),
        "mean": np.mean(total_fuel_values),
        "median": np.median(total_fuel_values),
        "std": np.std(total_fuel_values, ddof=1),
        "q1": np.percentile(total_fuel_values, 25),
        "q3": np.percentile(total_fuel_values, 75),
        "iqr": (
            np.percentile(total_fuel_values, 75)
            - np.percentile(total_fuel_values, 25)
        ),
        "min": np.min(total_fuel_values),
        "max": np.max(total_fuel_values),
    }
# ============================================================
# LATEX TABLE: TOTAL MISSION FUEL-BURN DISPERSION
# ============================================================

print(r"\begin{table}[H]")
print(r"\centering")
print(r"\small")
print(
    r"\caption{Total mission fuel-burn statistics by bypass-ratio group.}"
)
print(r"\label{tab:mission_fuel_burn_statistics_BPR}")
print(r"\begin{tabular}{lrrrrrr}")
print(r"\hline")
print(
    r"\textbf{BPR group} & "
    r"\textbf{N} & "
    r"\textbf{Mean [kg]} & "
    r"\textbf{Median [kg]} & "
    r"\textbf{SD [kg]} & "
    r"\textbf{IQR [kg]} & "
    r"\textbf{Range [kg]} \\"
)
print(r"\hline")

for group_name, stats in mission_fuel_statistics.items():

    print(
        f"{group_name} & "
        f"{stats['N']} & "
        f"{stats['mean']:.1f} & "
        f"{stats['median']:.1f} & "
        f"{stats['std']:.1f} & "
        f"{stats['iqr']:.1f} & "
        f"{stats['min']:.1f}--{stats['max']:.1f} \\\\"
    )

print(r"\hline")
print(r"\end{tabular}")
print(r"\end{table}")

# ============================================================
# TOTAL MISSION FUEL-BURN DISTRIBUTION BY BPR GROUP
# ============================================================

mission_fuel_boxplot = []

mission_fuel_labels = []

for bpr_min, bpr_max, group_name in BPR_BANDS:

    values = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:

            result = mission_results[name]

            total_fuel = (
                result["lto_fuel_burn_kg"]
                + result["climb_fuel_burn_kg"]
                + result["cruise_fuel_burn_kg"]
                + result["descent_fuel_burn_kg"]
            )

            if np.isfinite(total_fuel):
                values.append(total_fuel)

    mission_fuel_boxplot.append(values)
    mission_fuel_labels.append(group_name)


fig, ax = plt.subplots(
    figsize=FIG_SINGLE
)

ax.boxplot(
    mission_fuel_boxplot,
    tick_labels=mission_fuel_labels,
    showfliers=True
)

ax.set_xlabel(
    "Bypass-ratio group",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Total mission fuel burn [kg]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        plot_folder,
        "total_mission_fuel_burn_distribution_by_BPR.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# LTO FUEL BURN ERROR VS BPR
# ============================================================

fig, ax = plt.subplots(
    figsize=FIG_SINGLE
)


# ------------------------------------------------------------
# Plot each BPR group
# ------------------------------------------------------------

for bpr_min, bpr_max, label in BPR_BANDS:

    mask = (
        (lto_error_df["BPR"] >= bpr_min)
        & (lto_error_df["BPR"] < bpr_max)
    )

    group = lto_error_df.loc[mask]

    if group.empty:
        continue

    ax.scatter(
        group["BPR"],
        group["error_percent"],
        s=55,
        label=label,
    )


# ------------------------------------------------------------
# Zero-error reference
# ------------------------------------------------------------

ax.axhline(
    0,
    linestyle="--",
    linewidth=1.5,
)


# ------------------------------------------------------------
# Formatting
# ------------------------------------------------------------

ax.set_xlabel(
    "Bypass ratio (BPR)",
    fontsize=LABEL_SIZE
)

ax.set_ylabel(
    "Total LTO fuel-burn error [%]",
    fontsize=LABEL_SIZE
)

ax.tick_params(
    axis="both",
    labelsize=TICK_SIZE
)

ax.grid(
    True,
    alpha=0.3
)

ax.legend(
    title="Bypass ratio",
    fontsize=LEGEND_SIZE
)

plt.tight_layout()


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

plt.savefig(
    os.path.join(
        plot_folder,
        "LTO_fuel_burn_error_vs_BPR.png",
    ),
    dpi=300,
    bbox_inches="tight",
)

plt.show()
plt.close()

# ============================================================
# TOTAL MISSION EMISSIONS STATISTICS BY BPR GROUP
# ============================================================

emission_rows = []

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        if name not in mission_emissions_summary_df.columns:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    for pollutant in ["NOx", "CO", "HC"]:

        values = []

        for name in selected_engines:

            phase_rows = {
                "LTO": f"LTO_{pollutant}_kg",
                "Climb": f"CLIMB_{pollutant}_kg",
                "Cruise": f"CRUISE_{pollutant}_kg",
                "Descent": f"DESCENT_{pollutant}_kg",
            }

            total = 0.0

            for row_name in phase_rows.values():

                value = mission_emissions_summary_df.loc[
                    row_name,
                    name
                ]

                if np.isfinite(value):
                    total += value

            if np.isfinite(total):
                values.append(total)

        values = np.array(values)

        if len(values) == 0:
            continue

        emission_rows.append({
            "BPR": group_name,
            "pollutant": pollutant,
            "N": len(values),
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values, ddof=1),
            "iqr": (
                np.percentile(values, 75)
                - np.percentile(values, 25)
            ),
        })

# ============================================================
# LATEX TABLE: TOTAL MISSION EMISSION STATISTICS
# ============================================================

print(r"\begin{table}[H]")
print(r"\centering")
print(r"\small")
print(
    r"\caption{Total mission emission statistics by bypass-ratio group.}"
)
print(r"\label{tab:mission_emissions_statistics_BPR}")
print(r"\begin{tabular}{llrrrr}")
print(r"\hline")
print(
    r"\textbf{BPR group} & "
    r"\textbf{Pollutant} & "
    r"\textbf{N} & "
    r"\textbf{Mean [kg]} & "
    r"\textbf{Median [kg]} & "
    r"\textbf{IQR [kg]} \\"
)
print(r"\hline")

for row in emission_rows:

    print(
        f"{row['BPR']} & "
        f"{row['pollutant']} & "
        f"{row['N']} & "
        f"{row['mean']:.2f} & "
        f"{row['median']:.2f} & "
        f"{row['iqr']:.2f} \\\\"
    )

print(r"\hline")
print(r"\end{tabular}")
print(r"\end{table}")

# ============================================================
# AVERAGE LTO FUEL BURN BY BPR GROUP AND LTO PHASE
# ============================================================

import pandas as pd
import numpy as np

# ------------------------------------------------------------
# 1. Define the BPR groups
# ------------------------------------------------------------

bpr_bins = [4, 6, 8, 10, 12]
bpr_labels = ["BPR 4-6", "BPR 6-8", "BPR 8-10", "BPR 10-12"]


# ------------------------------------------------------------
# 2. Create a dataframe from your engine results
# ------------------------------------------------------------
# Replace the variable names below with the names already used
# in your code for:
#   - BPR
#   - TO fuel burn
#   - climb-out fuel burn
#   - approach fuel burn
#   - idle fuel burn
#
# Each row = one simulated engine.
print("\nDATAFRAMES CONTAINING LTO FUEL-BURN DATA:")
for name, obj in globals().items():
    if isinstance(obj, pd.DataFrame):
        cols = [str(c).lower() for c in obj.columns]
        if any("takeoff" in c or "climb" in c or "approach" in c or "idle" in c
               for c in cols):
            print("\n", name)
            print(obj.columns.tolist())



LTO_fuel_burn_df = pd.DataFrame({
    "BPR": BPR_results,
    "Take-off": fuel_burn_takeoff,
    "Climb-out": fuel_burn_climbout,
    "Approach": fuel_burn_approach,
    "Idle": fuel_burn_idle,
})


# ------------------------------------------------------------
# 3. Assign each engine to a BPR group
# ------------------------------------------------------------

LTO_fuel_burn_df["BPR group"] = pd.cut(
    LTO_fuel_burn_df["BPR"],
    bins=bpr_bins,
    labels=bpr_labels,
    right=False
)


# ------------------------------------------------------------
# 4. Calculate total LTO fuel burn for each engine
# ------------------------------------------------------------

LTO_fuel_burn_df["Total"] = (
    LTO_fuel_burn_df["Take-off"]
    + LTO_fuel_burn_df["Climb-out"]
    + LTO_fuel_burn_df["Approach"]
    + LTO_fuel_burn_df["Idle"]
)


# ------------------------------------------------------------
# 5. Calculate the average fuel burn for each BPR group
# ------------------------------------------------------------

average_LTO_fuel_burn = (
    LTO_fuel_burn_df
    .groupby("BPR group", observed=True)[
        ["Take-off", "Climb-out", "Approach", "Idle", "Total"]
    ]
    .mean()
    .reindex(bpr_labels)
)


# ------------------------------------------------------------
# 6. Print the table
# ------------------------------------------------------------

print("\n============================================================")
print("AVERAGE LTO FUEL BURN BY BPR GROUP")
print("============================================================")

print(
    average_LTO_fuel_burn
    .round(1)
    .to_string()
)


# ------------------------------------------------------------
# 7. LaTeX-ready table
# ------------------------------------------------------------

latex_table = average_LTO_fuel_burn.round(1).to_latex(
    index=True,
    header=True,
    float_format="%.1f",
    column_format="lrrrrr"
)

print("\nLaTeX table:")
print(latex_table)

# ============================================================
# AVERAGE LTO FUEL BURN BY BPR GROUP AND LTO PHASE
# ============================================================

LTO_fuel_burn_by_BPR_phase = {}

for bpr_min, bpr_max, group_name in BPR_BANDS:

    selected_engines = []

    for name, data in engines.items():

        if name not in mission_results:
            continue

        BPR = data["engine"]["BPR"]

        if bpr_min <= BPR < bpr_max:
            selected_engines.append(name)

    if selected_engines:

        LTO_fuel_burn_by_BPR_phase[group_name] = {

            "N": len(selected_engines),

            "Take-off": np.mean([
                mission_results[name]["takeoff_fuel_burn_kg"]
                for name in selected_engines
            ]),

            "Climb-out": np.mean([
                mission_results[name]["climbout_fuel_burn_kg"]
                for name in selected_engines
            ]),

            "Approach": np.mean([
                mission_results[name]["approach_fuel_burn_kg"]
                for name in selected_engines
            ]),

            "Idle": np.mean([
                mission_results[name]["idle_fuel_burn_kg"]
                for name in selected_engines
            ]),

            "LTO total": np.mean([
                mission_results[name]["lto_fuel_burn_kg"]
                for name in selected_engines
            ]),
        }

# ------------------------------------------------------------
# PRINT RESULTS
# ------------------------------------------------------------
