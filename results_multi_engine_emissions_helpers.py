# ============================================================
# EMISSIONS FUNCTIONS
# ============================================================

import numpy as np


LTO_POINT_ORDER = ["idle", "approach", "climbout", "takeoff"]


# ============================================================
# P3T3 REFERENCE DATA
# ============================================================

def build_P3T3_reference(
    operating_results,
    ICAO_EI_species,
    species,
):
    """
    Build a species-specific P3T3 reference dataset from the ICAO LTO
    operating points for one engine.

    Parameters
    ----------
    operating_results : dict
        Results from the off-design engine simulation for one engine.

    ICAO_EI_species : dict
        ICAO emission indices in g/kg fuel for one species, keyed by
        LTO operating point name, for example:
            {
                "idle": ...,
                "approach": ...,
                "climbout": ...,
                "takeoff": ...,
            }

    species : str
        "NOx", "CO", or "HC".

    Returns
    -------
    reference_data : dict
        Contains T03, P03 and the species-specific reference EI for each
        LTO point.
    """

    if species not in ["NOx", "CO", "HC"]:
        raise ValueError(
            f"Unsupported species '{species}'. Use 'NOx', 'CO', or 'HC'."
        )

    reference_data = {}

    for name in LTO_POINT_ORDER:
        if name not in operating_results:
            continue
        if name not in ICAO_EI_species:
            continue

        result = operating_results[name]

        reference_data[name] = {
            "T03": result["T03"],
            "P03": result["P03"],
            f"EI_{species}": ICAO_EI_species[name],
        }

    return reference_data


# ============================================================
# REFERENCE EI INTERPOLATION
# ============================================================

def interpolate_EI_T3(
    T03,
    reference_data,
    species,
):
    """
    Interpolate the reference emission index as a function of combustor
    inlet stagnation temperature T03.
    """

    T3_values = np.array([
        reference_data["idle"]["T03"],
        reference_data["approach"]["T03"],
        reference_data["climbout"]["T03"],
        reference_data["takeoff"]["T03"],
    ])

    EI_values = np.array([
        reference_data["idle"][f"EI_{species}"],
        reference_data["approach"][f"EI_{species}"],
        reference_data["climbout"][f"EI_{species}"],
        reference_data["takeoff"][f"EI_{species}"],
    ])

    return np.interp(
        T03,
        T3_values,
        EI_values,
    )


# ============================================================
# REFERENCE P03 INTERPOLATION
# ============================================================

def interpolate_P03_reference(
    T03,
    reference_data,
):
    """
    Determine the reference combustor inlet stagnation pressure
    corresponding to a given T03.
    """

    T3_values = np.array([
        reference_data["idle"]["T03"],
        reference_data["approach"]["T03"],
        reference_data["climbout"]["T03"],
        reference_data["takeoff"]["T03"],
    ])

    P3_values = np.array([
        reference_data["idle"]["P03"],
        reference_data["approach"]["P03"],
        reference_data["climbout"]["P03"],
        reference_data["takeoff"]["P03"],
    ])

    return np.interp(
        T03,
        T3_values,
        P3_values,
    )


# ============================================================
# P3T3 EMISSION INDEX
# ============================================================

def calculate_EI_P3T3(
    T03,
    P03,
    reference_data,
    species,
    pressure_exponent_NOx=0.4,
    pressure_exponent_CO=1.0,
    pressure_exponent_HC=1.0,
):
    """
    Calculate the pollutant emission index using the P3T3 methodology.

    NOx:
        EI = EI_ref * (P03 / P03_ref)^0.4

    CO / HC:
        EI = EI_ref * (P03_ref / P03)^1.0
    """

    if species not in ["NOx", "CO", "HC"]:
        raise ValueError(
            f"Unsupported species '{species}'. Use 'NOx', 'CO', or 'HC'."
        )

    EI_reference = interpolate_EI_T3(
        T03=T03,
        reference_data=reference_data,
        species=species,
    )

    P03_reference = interpolate_P03_reference(
        T03=T03,
        reference_data=reference_data,
    )

    if P03 <= 0:
        raise ValueError(f"Invalid modelled P03: {P03}")
    if P03_reference <= 0:
        raise ValueError(f"Invalid reference P03: {P03_reference}")

    if species == "NOx":
        EI = (
            EI_reference
            * (P03 / P03_reference) ** pressure_exponent_NOx
        )
    else:
        pressure_exponent = (
            pressure_exponent_CO if species == "CO" else pressure_exponent_HC
        )
        EI = (
            EI_reference
            * (P03_reference / P03) ** pressure_exponent
        )

    return EI


# ============================================================
# GENERIC POLLUTANT CALCULATION
# ============================================================

def calculate_emissions(
    operating_results,
    operating_points,
    reference_data,
    species,
    pressure_exponent_NOx=0.4,
    pressure_exponent_CO=1.0,
    pressure_exponent_HC=1.0,
):
    """
    Calculate emissions for NOx, CO or HC using the P3T3 methodology.
    """

    emissions_results = {}

    for name, result in operating_results.items():
        fuel_mass_flow = result["fuel_mass_flow"]
        duration = operating_points[name]["time"]

        EI = calculate_EI_P3T3(
            T03=result["T03"],
            P03=result["P03"],
            reference_data=reference_data,
            species=species,
            pressure_exponent_NOx=pressure_exponent_NOx,
            pressure_exponent_CO=pressure_exponent_CO,
            pressure_exponent_HC=pressure_exponent_HC,
        )

        emission_mass_flow_kg_s = EI * fuel_mass_flow / 1000.0
        emission_mass = emission_mass_flow_kg_s * duration

        emissions_results[name] = {
            "EI": EI,
            "emission_mass_flow": emission_mass_flow_kg_s,
            "emission_mass": emission_mass,
        }

    return emissions_results


# ============================================================
# COMPLETE ENGINE EMISSIONS CALCULATION
# ============================================================

def calculate_engine_emissions(
    engine_name,
    operating_results,
    operating_points,
    ICAO_EI,
    P3T3_reference_by_species=None,
    pressure_exponent_NOx=0.4,
    pressure_exponent_CO=1.0,
    pressure_exponent_HC=1.0,
):
    """
    Calculate NOx, CO and HC emissions over the LTO cycle using a
    species-specific P3T3 framework.

    Parameters
    ----------
    ICAO_EI : dict
        Expected structure:
            {
                "NOx": {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
                "CO":  {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
                "HC":  {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
            }

    P3T3_reference_by_species : dict, optional
        Expected structure:
            {
                "NOx": <reference_data>,
                "CO":  <reference_data>,
                "HC":  <reference_data>,
            }

        If omitted, the reference datasets are built internally from
        operating_results and ICAO_EI.
    """

    print("")
    print("=" * 60)
    print(f"EMISSIONS: {engine_name}")
    print("=" * 60)

    if P3T3_reference_by_species is None:
        P3T3_reference_by_species = {
            species: build_P3T3_reference(
                operating_results=operating_results,
                ICAO_EI_species=ICAO_EI[species],
                species=species,
            )
            for species in ["NOx", "CO", "HC"]
        }

    NOx = calculate_emissions(
        operating_results=operating_results,
        operating_points=operating_points,
        reference_data=P3T3_reference_by_species["NOx"],
        species="NOx",
        pressure_exponent_NOx=pressure_exponent_NOx,
        pressure_exponent_CO=pressure_exponent_CO,
        pressure_exponent_HC=pressure_exponent_HC,
    )

    CO = calculate_emissions(
        operating_results=operating_results,
        operating_points=operating_points,
        reference_data=P3T3_reference_by_species["CO"],
        species="CO",
        pressure_exponent_NOx=pressure_exponent_NOx,
        pressure_exponent_CO=pressure_exponent_CO,
        pressure_exponent_HC=pressure_exponent_HC,
    )

    HC = calculate_emissions(
        operating_results=operating_results,
        operating_points=operating_points,
        reference_data=P3T3_reference_by_species["HC"],
        species="HC",
        pressure_exponent_NOx=pressure_exponent_NOx,
        pressure_exponent_CO=pressure_exponent_CO,
        pressure_exponent_HC=pressure_exponent_HC,
    )

    total_NOx = sum(result["emission_mass"] for result in NOx.values())
    total_CO = sum(result["emission_mass"] for result in CO.values())
    total_HC = sum(result["emission_mass"] for result in HC.values())

    print(f"Total LTO NOx = {total_NOx:.3f} kg")
    print(f"Total LTO CO  = {total_CO:.3f} kg")
    print(f"Total LTO HC  = {total_HC:.3f} kg")

    return {
        "NOx": NOx,
        "CO": CO,
        "HC": HC,
        "total_NOx": total_NOx,
        "total_CO": total_CO,
        "total_HC": total_HC,
    }


# ============================================================
# ICAO EI EXTRACTION
# ============================================================

def build_icao_ei_by_engine(icao_data):
    """
    Build engine-wise ICAO EI dictionaries from icao_data.

    Expected input structure per engine:
        {
            "nox_ei": {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
            "co_ei":  {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
            "hc_ei":  {"idle": ..., "approach": ..., "climbout": ..., "takeoff": ...},
        }
    """

    out = {}

    for name, row in icao_data.items():
        if not all(k in row for k in ["nox_ei", "co_ei", "hc_ei"]):
            continue

        out[name] = {
            "NOx": {
                key: row["nox_ei"].get(key)
                for key in LTO_POINT_ORDER
            },
            "CO": {
                key: row["co_ei"].get(key)
                for key in LTO_POINT_ORDER
            },
            "HC": {
                key: row["hc_ei"].get(key)
                for key in LTO_POINT_ORDER
            },
        }

    return out


# ============================================================
# MULTI-ENGINE P3T3 REFERENCE
# ============================================================

def build_p3t3_reference_for_all_engines(
    lto_results,
    icao_ei_by_engine,
    build_P3T3_reference_func=None,
    species_list=None,
):
    """
    Build species-specific P3T3 reference datasets for every engine.
    """

    species_list = species_list or ["NOx", "CO", "HC"]
    build_func = build_P3T3_reference_func or build_P3T3_reference

    out = {}

    for name, operating_results in lto_results.items():
        if name not in icao_ei_by_engine:
            continue

        out[name] = {}

        for species in species_list:
            out[name][species] = build_func(
                operating_results=operating_results,
                ICAO_EI_species=icao_ei_by_engine[name][species],
                species=species,
            )

    return out


# ============================================================
# MULTI-ENGINE EMISSIONS
# ============================================================

def calculate_emissions_for_all_engines(
    engines,
    lto_results,
    operating_points,
    icao_data,
    calculate_engine_emissions_func=None,
    build_P3T3_reference_func=None,
    species_list=None,
):
    """
    Run the full species-specific P3T3 emissions workflow for all engines.

    Returns
    -------
    ICAO_EI_by_engine : dict
    P3T3_reference_by_engine : dict
    all_engine_emissions : dict
    """

    species_list = species_list or ["NOx", "CO", "HC"]
    calc_func = calculate_engine_emissions_func or calculate_engine_emissions

    icao_ei_by_engine = build_icao_ei_by_engine(icao_data)

    p3t3_reference_by_engine = build_p3t3_reference_for_all_engines(
        lto_results=lto_results,
        icao_ei_by_engine=icao_ei_by_engine,
        build_P3T3_reference_func=build_P3T3_reference_func,
        species_list=species_list,
    )

    all_engine_emissions = {}

    for name in engines.keys():
        if name not in lto_results:
            continue
        if name not in icao_ei_by_engine:
            print(f"Skipping {name}: no ICAO EI data found.")
            continue

        all_engine_emissions[name] = calc_func(
            engine_name=name,
            operating_results=lto_results[name],
            operating_points=operating_points,
            ICAO_EI=icao_ei_by_engine[name],
            P3T3_reference_by_species=p3t3_reference_by_engine.get(name),
        )

    return icao_ei_by_engine, p3t3_reference_by_engine, all_engine_emissions


# ============================================================
# TOTAL MODELLED EMISSIONS [kg]
# ============================================================

def build_total_emissions_kg_df(all_engine_emissions):
    """
    Build a DataFrame of total modelled LTO emissions in kg.

    Rows:
        NOx_kg, CO_kg, HC_kg
    Columns:
        engine names
    """

    totals = {}

    for name, engine_emissions in all_engine_emissions.items():
        totals[name] = {
            "NOx_kg": sum(
                x["emission_mass"]
                for x in engine_emissions.get("NOx", {}).values()
                if isinstance(x, dict) and "emission_mass" in x
            ),
            "CO_kg": sum(
                x["emission_mass"]
                for x in engine_emissions.get("CO", {}).values()
                if isinstance(x, dict) and "emission_mass" in x
            ),
            "HC_kg": sum(
                x["emission_mass"]
                for x in engine_emissions.get("HC", {}).values()
                if isinstance(x, dict) and "emission_mass" in x
            ),
        }

    return np.nan if not totals else __import__("pandas").DataFrame(totals)


# ============================================================
# ICAO TOTAL EMISSIONS [kg]
# ============================================================

def build_icao_total_emissions_kg_df(
    engine_names,
    icao_data,
):
    """
    Build a DataFrame of ICAO total LTO emissions in kg from the databank
    total grams values.
    """

    pd = __import__("pandas")
    totals = {}

    for name in engine_names:
        row = icao_data.get(name)
        if row is None:
            continue
        if not all(k in row for k in ["nox_ei", "co_ei", "hc_ei"]):
            continue

        totals[name] = {
            "NOx_kg": (
                None if row["nox_ei"].get("lto_total_g") is None
                else row["nox_ei"]["lto_total_g"] / 1000.0
            ),
            "CO_kg": (
                None if row["co_ei"].get("lto_total_g") is None
                else row["co_ei"]["lto_total_g"] / 1000.0
            ),
            "HC_kg": (
                None if row["hc_ei"].get("lto_total_g") is None
                else row["hc_ei"]["lto_total_g"] / 1000.0
            ),
        }

    return pd.DataFrame(totals)


# ============================================================
# EMISSIONS PERCENT DIFFERENCE
# ============================================================

def compute_total_lto_emissions_percent_difference_df(
    model_total_emissions_kg_df,
    icao_total_emissions_kg_df,
):
    """
    Compute percent difference between modelled and ICAO total LTO masses.

    Output rows:
        NOx_%, CO_%, HC_%
    """

    pd = __import__("pandas")
    out = {}

    if not hasattr(model_total_emissions_kg_df, "columns"):
        return pd.DataFrame()

    for name in model_total_emissions_kg_df.columns:
        if name not in icao_total_emissions_kg_df.columns:
            continue

        out[name] = {}

        for kg_row, pct_row in [
            ("NOx_kg", "NOx_%"),
            ("CO_kg", "CO_%"),
            ("HC_kg", "HC_%"),
        ]:
            model_value = model_total_emissions_kg_df.loc[kg_row, name]
            icao_value = icao_total_emissions_kg_df.loc[kg_row, name]

            if pd.isna(icao_value) or icao_value == 0:
                out[name][pct_row] = None
            else:
                out[name][pct_row] = (
                    (model_value - icao_value)
                    / icao_value
                    * 100.0
                )

    return pd.DataFrame(out)
