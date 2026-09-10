# Turbofan Cycle Analysis and Emissions Modelling

Python-based turbofan engine performance and emissions modelling framework developed as part of an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

The model provides a modular framework for turbofan cycle analysis, operating-point and off-design simulations, fuel-flow prediction, emissions analysis, and comparison with ICAO reference data. Results can be analysed across multiple engine configurations and visualised through dedicated plotting and results-processing modules.

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

## Main scripts

There are three main scripts used to run the different parts of the analysis:

* `main_results_plots.py` – runs the main engine simulations and generates the performance and comparison plots.
* `main_results_emissions.py` – runs the emissions analysis and generates the corresponding results and plots.
* `main_results_statistics.py` – performs the statistical analysis of the model results and reference data.

The remaining Python files contain the functions, engine data and supporting calculations called by these three scripts.

## Code structure

### Cycle model

* `cycle.py` – turbofan cycle calculations.
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

The model was developed and tested using Python 3.11.14. The code requires the packages listed in `requirements.txt`.

Install the required packages with:

```bash
pip install -r requirements.txt
```

### Performance simulations and plots

Run:

```bash
python main_results_plots.py
```
This is the main entry point for running the performance simulations and generating the associated plots and results.

### Emissions analysis

Run:

```bash
python main_results_emissions.py
```
This runs the emissions-related calculations and generates the corresponding results and visualisations.

### Statistical analysis

Run:

```bash
python main_results_statistics.py
```
This performs the statistical analysis used to evaluate the model results and their agreement with the reference data.

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

## Reference Data

The repository contains engine and ICAO reference datasets used for model development and validation.

Where reference data are unavailable, additional engine data or assumptions may be required. These cases are handled through dedicated data modules.

The assumptions and data sources used in the model are described in greater detail in the associated MSc project report.

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

## Project context

This repository contains code developed as part of an MSc research project in Advanced Aeronautical Engineering at Imperial College London.

The project focuses on turbofan engine performance and emissions modelling, with particular emphasis on the development of a Python-based computational framework and validation against available reference data.

For a detailed description of the theoretical background, modelling assumptions, methodology and results, please refer to the associated project report.

## Author

**Thanyamone Besson**

MSc Advanced Aeronautical Engineering

Imperial College London

## Disclaimer

This software was developed for academic and research purposes. Engine parameters, reference data and modelling assumptions may rely on publicly available information and engineering approximations. The results should therefore not be interpreted as representing proprietary engine models or manufacturer-certified performance data.

