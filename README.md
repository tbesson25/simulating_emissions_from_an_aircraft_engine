# Turbofan Cycle Analysis and Emissions Modelling

Python-based turbofan engine performance and emissions modelling framework developed as part of an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

The model provides a modular framework for turbofan cycle analysis, operating-point and off-design simulations, fuel-flow prediction, emissions analysis, and comparison with ICAO reference data. Results can be analysed across multiple engine configurations and visualised through dedicated plotting and results-processing modules.

---

## Project Overview

The objective of the project is to develop a Python-based turbofan model capable of:

* modelling turbofan thermodynamic cycles;
* evaluating engine performance at different operating conditions;
* performing off-design simulations;
* estimating fuel mass flow and related performance quantities;
* analysing aircraft-engine emissions;
* comparing model predictions with ICAO reference data;
* evaluating model accuracy using statistical analysis; and
* generating plots and tables for analysis and reporting.

The code is organised into modular components for engine definition, thermodynamic calculations, operating-point simulations, off-design modelling, data handling, and results visualisation.

---

## Repository Structure

The repository contains three main entry-point scripts:

| Main script                  | Purpose                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------- |
| `main_results_plots.py`      | Main simulation and results script for generating performance results and plots |
| `main_results_emissions.py`  | Main script for emissions-related analysis and visualisation                    |
| `main_results_statistics.py` | Main script for statistical analysis and model validation                       |

These scripts call the supporting modules described below.

### Core cycle model

| Module               | Purpose                                                       |
| -------------------- | ------------------------------------------------------------- |
| `cumpsty_cycle.py`   | Turbofan cycle calculations based on the Cumpsty approach     |
| `cycle_functions.py` | Common thermodynamic and turbofan cycle calculation functions |

### Engine definition and data

| Module                                 | Purpose                                                               |
| -------------------------------------- | --------------------------------------------------------------------- |
| `engine_definition.py`                 | Definition and configuration of the engine models                     |
| `engine_parameters.py`                 | Engine performance and design parameters                              |
| `engine_ICAO_data.py`                  | ICAO reference engine data                                            |
| `engine_ICAO_data_missing_high_BPR.py` | Additional ICAO/reference data for engines with missing high-BPR data |
| `engine_missing_data_mid_bpr.py`       | Additional engine data for cases with missing mid-BPR data            |

### Operating-point simulations

| Module                           | Purpose                                                        |
| -------------------------------- | -------------------------------------------------------------- |
| `operating_points.py`            | Definition of engine operating points                          |
| `operating_points_simulation.py` | Simulation of engine performance at specified operating points |
| `atmosphere.py`                  | Atmospheric property calculations                              |

### Off-design modelling

| Module                                          | Purpose                                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `off_design_simulation_simultaneous_FPR_T04.py` | Main off-design simulation involving simultaneous FPR and turbine inlet temperature calculations |
| `off_design_simultaneous_solver.py`             | Numerical solver used within the off-design calculation                                          |
| `off_design.py`                                 | Supporting off-design thermodynamic calculations                                                 |

### Engine geometry

| Module            | Purpose                                                              |
| ----------------- | -------------------------------------------------------------------- |
| `engine_areas.py` | Calculation of engine flow areas and associated geometric quantities |

### Results and visualisation

| Module                                      | Purpose                                               |
| ------------------------------------------- | ----------------------------------------------------- |
| `results_multi_engine_emissions_helpers.py` | Helper functions for multi-engine emissions results   |
| `results_mission_helpers.py`                | Helper functions for mission-level results            |
| `results_mission_emissions_helpers.py`      | Helper functions for mission-level emissions analysis |
| `results_table_helpers_all.py`              | Helper functions for generating results tables        |

---

## Code Dependency

The three main scripts act as the primary entry points to the model.

A simplified representation of the code structure is:

```text
                         ┌──────────────────────────────┐
                         │       MAIN ENTRY POINTS      │
                         └──────────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
    main_results_plots.py   main_results_emissions.py   main_results_statistics.py
                │                     │                     │
                └─────────────────────┼─────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │   Simulation Modules   │
                         ├────────────────────────┤
                         │ operating_points      │
                         │ operating_points_      │
                         │ simulation             │
                         │ off_design             │
                         │ atmosphere             │
                         │ engine_areas           │
                         └────────────┬───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │   Cycle Model          │
                         ├────────────────────────┤
                         │ cumpsty_cycle          │
                         │ cycle_functions        │
                         └────────────┬───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │ Engine Definitions &   │
                         │ Reference Data         │
                         ├────────────────────────┤
                         │ engine_definition      │
                         │ engine_parameters      │
                         │ engine_ICAO_data       │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │ Results & Visualisation│
                         ├────────────────────────┤
                         │ results_*_helpers      │
                         └────────────────────────┘
```

---

## Installation

### Requirements

The model requires Python 3.x and the Python packages listed in:

```text
requirements.txt
```

Install the dependencies using:

```bash
pip install -r requirements.txt
```

---

## Running the Model

The repository has three main execution scripts.

### 1. Performance simulations and plots

Run:

```bash
python main_results_plots.py
```

This is the main entry point for running the performance simulations and generating the associated plots and results.

### 2. Emissions analysis

Run:

```bash
python main_results_emissions.py
```

This runs the emissions-related calculations and generates the corresponding results and visualisations.

### 3. Statistical analysis

Run:

```bash
python main_results_statistics.py
```

This performs the statistical analysis used to evaluate the model results and their agreement with the reference data.

---

## Model Workflow

The general computational workflow is:

```text
Engine definition
       ↓
Engine parameters and reference data
       ↓
Operating-point definition
       ↓
Atmospheric conditions
       ↓
Turbofan cycle calculation
       ↓
Performance calculation
       ↓
Off-design simulation (where applicable)
       ↓
Fuel-flow and emissions calculations
       ↓
Comparison with reference data
       ↓
Results processing
       ↓
Plots, tables and statistical analysis
```

---

## Model Components

### Turbofan cycle analysis

The model includes thermodynamic calculations for the main turbofan engine stations and components, including the fan, compressor, combustor, turbines and nozzles.

The cycle model uses the relevant thermodynamic and component performance parameters to calculate engine performance quantities under the specified operating conditions.

### Operating-point analysis

The model can evaluate engine performance at defined operating points representing different flight or engine conditions.

### Off-design analysis

An off-design modelling framework is included to evaluate engine behaviour away from the design condition.

The off-design calculation includes a simultaneous solution involving fan pressure ratio and turbine inlet temperature, together with the associated numerical solver.

### Emissions analysis

The model estimates emissions-related quantities and allows the results to be compared with available ICAO reference data.

### Statistical analysis

Statistical analysis is used to quantify the agreement between model predictions and reference data.

---

## Reference Data

The repository contains engine and ICAO reference datasets used for model development and validation.

Where reference data are unavailable, additional engine data or assumptions may be required. These cases are handled through dedicated data modules.

The assumptions and data sources used in the model are described in greater detail in the associated MSc project report.

---

## Results

The model produces:

* engine performance results;
* fuel-flow predictions;
* emissions-related results;
* comparisons with ICAO reference data;
* multi-engine comparisons;
* mission-level results;
* statistical validation metrics;
* plots; and
* results tables.

The `results_*_helpers.py` modules provide supporting functions for processing and visualising these results.

---

## Reproducibility

To reproduce the main analyses:

1. Clone or download this repository.
2. Install the dependencies listed in `requirements.txt`.
3. Run the relevant main script:

   ```bash
   python main_results_plots.py
   ```

   or

   ```bash
   python main_results_emissions.py
   ```

   or

   ```bash
   python main_results_statistics.py
   ```
4. The resulting simulations, plots and statistical analyses can then be examined or further processed.

Specific engine selections, operating conditions and modelling assumptions are defined within the corresponding configuration and data modules.

---

## Project Context

This repository contains code developed for an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

The project focuses on turbofan engine performance and emissions modelling, with particular emphasis on the development of a Python-based computational framework and validation against available reference data.

For a detailed description of the theoretical background, modelling assumptions, methodology and results, please refer to the associated project report.

---

## Author

**Thanyamone Besson**

MSc Advanced Aeronautical Engineering
Imperial College London

---

## Disclaimer

This software was developed for academic and research purposes. Engine parameters, reference data and modelling assumptions may rely on publicly available information and engineering approximations. The results should therefore not be interpreted as representing proprietary engine models or manufacturer-certified performance data.
