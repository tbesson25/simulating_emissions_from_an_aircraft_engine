# Turbofan Cycle Analysis and Emissions Modelling

Python code developed for an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

The project focuses on turbofan cycle analysis, engine performance and off-design modelling, fuel-flow prediction, and emissions analysis. Model results are compared with available ICAO reference data and further evaluated using statistical analysis.

## Main scripts

There are three main scripts used to run the different parts of the analysis:

* `main_results_plots.py` – runs the main engine simulations and generates the performance and comparison plots.
* `main_results_emissions.py` – runs the emissions analysis and generates the corresponding results and plots.
* `main_results_statistics.py` – performs the statistical analysis of the model results and reference data.

The remaining Python files contain the functions, engine data and supporting calculations called by these three scripts.

## Code structure

### Cycle model

* `cumpsty_cycle.py` – turbofan cycle calculations based on the Cumpsty approach.
* `cycle_functions.py` – common thermodynamic and cycle calculation functions.

### Engine data

* `engine_definition.py` – engine definitions and configurations.
* `engine_parameters.py` – engine design and performance parameters.
* `engine_ICAO_data.py` – ICAO reference data.
* `engine_ICAO_data_missing_high_BPR.py` – additional data for engines with missing high-BPR reference data.
* `engine_missing_data_mid_bpr.py` – additional engine data for cases with missing mid-BPR data.

### Operating points and off-design

* `operating_points.py` – definition of the operating points used in the simulations.
* `operating_points_simulation.py` – operating-point simulations.
* `atmosphere.py` – atmospheric calculations.
* `off_design_simulation_simultaneous_FPR_T04.py` – off-design simulation with simultaneous FPR and T04 calculations.
* `off_design_simultaneous_solver.py` – numerical solver used for the off-design calculations.
* `off_design.py` – supporting off-design calculations.
* `engine_areas.py` – engine flow-area calculations.

### Results and visualisation

* `results_multi_engine_emissions_helpers.py`
* `results_mission_helpers.py`
* `results_mission_emissions_helpers.py`
* `results_table_helpers_all.py`

These modules contain helper functions used to process, organise and visualise the simulation results.

## How to run

### Requirements

The code requires Python 3.x and the packages listed in `requirements.txt`.

Install the required packages with:

```bash
pip install -r requirements.txt
```

### Main results and plots

Run:

```bash
python main_results_plots.py
```

### Emissions analysis

Run:

```bash
python main_results_emissions.py
```

### Statistical analysis

Run:

```bash
python main_results_statistics.py
```

The engine configurations, operating points and other model inputs are defined in the corresponding Python modules.

## Model workflow

The general workflow of the model is:

```text
Engine definition and parameters
            ↓
Operating-point definition
            ↓
Atmospheric conditions
            ↓
Turbofan cycle calculation
            ↓
Performance calculation
            ↓
Off-design simulation
            ↓
Fuel-flow and emissions analysis
            ↓
Comparison with ICAO reference data
            ↓
Results, plots and statistical analysis
```

Not every step is necessarily used by every analysis script.

## Results

The code produces engine performance and fuel-flow results, emissions-related results, comparisons with ICAO reference data, mission-level results, plots, tables and statistical analysis.

The exact results produced depend on the main script being run and the selected engine configurations and operating conditions.

## Project context

This code was developed as part of an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

For the theoretical background, modelling assumptions, methodology and detailed discussion of the results, please refer to the associated MSc project report.

## Author

**Thanyamone Besson**

MSc Advanced Aeronautical Engineering
Imperial College London
