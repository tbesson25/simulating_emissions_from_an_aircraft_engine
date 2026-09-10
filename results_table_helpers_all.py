"""Helpers to print wide comparison result tables with metadata rows.

This module supports a final mixed-format summary table grouped by BPR, with:
- metadata rows
- percent rows
- kg rows
- mission fuel-burn rows
- mission emissions rows
"""

from __future__ import annotations

from typing import Dict, List, Optional
import pandas as pd


DEFAULT_METADATA_LABELS = ["BPR", "OPR", "Thrust_kN", "D_m", "FPR", "FBPR"]
DEFAULT_PERCENT_ROWS = ["TOTAL_FUEL_BURN_%", "NOx_%", "CO_%", "HC_%"]
DEFAULT_KG_ROWS = [
    "NOx_kg",
    "CO_kg",
    "HC_kg",
    "LTO_FUEL_BURN_kg",
    "CLIMB_FUEL_BURN_kg",
    "CRUISE_1H_FUEL_BURN_kg",
    "DESCENT_FUEL_BURN_kg",
    "TOTAL_MISSION_FUEL_BURN_kg",
    "LTO_NOx_kg",
    "LTO_CO_kg",
    "LTO_HC_kg",
    "CLIMB_NOx_kg",
    "CLIMB_CO_kg",
    "CLIMB_HC_kg",
    "CRUISE_NOx_kg",
    "CRUISE_CO_kg",
    "CRUISE_HC_kg",
    "DESCENT_NOx_kg",
    "DESCENT_CO_kg",
    "DESCENT_HC_kg",
    "TOTAL_MISSION_NOx_kg",
    "TOTAL_MISSION_CO_kg",
    "TOTAL_MISSION_HC_kg",
]


def chunk_list(items: List[str], chunk_size: int) -> List[List[str]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def _normalize_key(name: str) -> str:
    text = str(name).strip().replace("__", "_")
    text = " ".join(text.upper().split())
    return text


def _candidate_keys(name: str) -> List[str]:
    raw = str(name).strip()
    n = _normalize_key(raw)
    keys = [n]
    if "_" in n:
        keys.append(n.replace("_", "__"))
    if "__" in n:
        keys.append(n.replace("__", "_"))
    if n.startswith("TRENT") and " " not in n[:8]:
        keys.append(n.replace("TRENT", "TRENT ", 1))
    if n.startswith("TRENT "):
        keys.append(n.replace("TRENT ", "TRENT", 1))
    seen = []
    for key in keys:
        if key not in seen:
            seen.append(key)
    return seen


def _lookup_with_normalization(source: Optional[Dict], engine_name: str):
    if not source:
        return None
    normalized_source = {_normalize_key(k): v for k, v in source.items()}
    for key in _candidate_keys(engine_name):
        if key in normalized_source:
            return normalized_source[key]
    return None


def _format_meta_value(value, decimals: int = 3) -> str:
    if value is None or pd.isna(value):
        return "None"
    if isinstance(value, float):
        text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
        return text if text else "0"
    return str(value)


def _percent_formatter(x) -> str:
    if x is None or pd.isna(x):
        return "None"
    return f"{x:+.0f}%"


def _kg_formatter(x) -> str:
    if x is None or pd.isna(x):
        return "None"
    return f"{x:.3f}"


def _bpr_band_label(bpr_value) -> str:
    if bpr_value is None or pd.isna(bpr_value):
        return "BPR UNKNOWN"
    if bpr_value < 2:
        return "BPR < 2"
    if bpr_value < 4:
        return "2 <= BPR < 4"
    if bpr_value < 6:
        return "4 <= BPR < 6"
    if bpr_value < 8:
        return "6 <= BPR < 8"
    if bpr_value < 10:
        return "8 <= BPR < 10"
    return "BPR >= 10"


def build_engine_metadata_from_sources(
    engine_names: List[str],
    icao_data: Optional[Dict[str, dict]] = None,
    engine_diameter_m: Optional[Dict[str, float]] = None,
    engine_cycle_defaults: Optional[Dict[str, dict]] = None,
) -> pd.DataFrame:
    rows = {
        "BPR": {},
        "OPR": {},
        "Thrust_kN": {},
        "D_m": {},
        "FPR": {},
        "FBPR": {},
    }

    for name in engine_names:
        icao_payload = _lookup_with_normalization(icao_data, name) or {}
        diameter = _lookup_with_normalization(engine_diameter_m, name)
        cycle_payload = _lookup_with_normalization(engine_cycle_defaults, name) or {}

        rows["BPR"][name] = icao_payload.get("bpr")
        rows["OPR"][name] = icao_payload.get("opr")
        rows["Thrust_kN"][name] = icao_payload.get("rated_thrust_kN")
        rows["D_m"][name] = diameter if diameter is not None else icao_payload.get("diameter_m", icao_payload.get("D"))
        rows["FPR"][name] = cycle_payload.get("FPR", icao_payload.get("FPR"))
        rows["FBPR"][name] = cycle_payload.get("FBPR", icao_payload.get("FBPR"))

    return pd.DataFrame(rows).T.reindex(columns=engine_names)


def make_mixed_display_table(
    printable: pd.DataFrame,
    meta_labels: Optional[List[str]] = None,
    percent_rows: Optional[List[str]] = None,
    kg_rows: Optional[List[str]] = None,
    metadata_decimals: int = 3,
) -> pd.DataFrame:
    meta_labels = meta_labels or DEFAULT_METADATA_LABELS
    percent_rows = percent_rows or DEFAULT_PERCENT_ROWS
    kg_rows = kg_rows or DEFAULT_KG_ROWS

    meta_set = set(meta_labels)
    percent_set = set(percent_rows)
    kg_set = set(kg_rows)

    display = pd.DataFrame(index=printable.index, columns=printable.columns, dtype=object)

    for row in printable.index:
        if row in meta_set:
            display.loc[row] = [
                _format_meta_value(printable.loc[row, col], decimals=metadata_decimals)
                for col in printable.columns
            ]
        elif row in kg_set:
            display.loc[row] = [
                _kg_formatter(printable.loc[row, col])
                for col in printable.columns
            ]
        elif row in percent_set or str(row).endswith("%"):
            display.loc[row] = [
                _percent_formatter(printable.loc[row, col])
                for col in printable.columns
            ]
        else:
            display.loc[row] = [
                _percent_formatter(printable.loc[row, col])
                for col in printable.columns
            ]

    return display


def _print_mixed_table(
    printable: pd.DataFrame,
    meta_labels: Optional[List[str]] = None,
    percent_rows: Optional[List[str]] = None,
    kg_rows: Optional[List[str]] = None,
    metadata_decimals: int = 3,
) -> None:
    if printable.empty:
        print("<empty table>")
        return
    display = make_mixed_display_table(
        printable,
        meta_labels=meta_labels,
        percent_rows=percent_rows,
        kg_rows=kg_rows,
        metadata_decimals=metadata_decimals,
    )
    print(display.to_string())


def build_total_emissions_kg_df(all_engine_emissions: Dict[str, dict]) -> pd.DataFrame:
    totals: Dict[str, Dict[str, float]] = {}
    for name, engine_emissions in all_engine_emissions.items():
        totals[name] = {
            "NOx_kg": sum(x["emission_mass"] for x in engine_emissions.get("NOx", {}).values()),
            "CO_kg": sum(x["emission_mass"] for x in engine_emissions.get("CO", {}).values()),
            "HC_kg": sum(x["emission_mass"] for x in engine_emissions.get("HC", {}).values()),
        }
    return pd.DataFrame(totals)


def build_combined_lto_summary_df(
    fuel_burn_percent_df: pd.DataFrame,
    emissions_percent_df: pd.DataFrame,
    emissions_kg_df: Optional[pd.DataFrame] = None,
    mission_fuel_burn_df: Optional[pd.DataFrame] = None,
    mission_emissions_kg_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    combined_rows = {}

    if "TOTAL" in fuel_burn_percent_df.index:
        combined_rows["TOTAL_FUEL_BURN_%"] = fuel_burn_percent_df.loc["TOTAL"]
    elif "TOTAL_FUEL_BURN_%" in fuel_burn_percent_df.index:
        combined_rows["TOTAL_FUEL_BURN_%"] = fuel_burn_percent_df.loc["TOTAL_FUEL_BURN_%"]

    for src, dst in [("NOx", "NOx_%"), ("CO", "CO_%"), ("HC", "HC_%")]:
        if src in emissions_percent_df.index:
            combined_rows[dst] = emissions_percent_df.loc[src]
        elif dst in emissions_percent_df.index:
            combined_rows[dst] = emissions_percent_df.loc[dst]

    if emissions_kg_df is not None:
        for row in ["NOx_kg", "CO_kg", "HC_kg"]:
            if row in emissions_kg_df.index:
                combined_rows[row] = emissions_kg_df.loc[row]

    if mission_fuel_burn_df is not None:
        for row in [
            "LTO_FUEL_BURN_kg",
            "CLIMB_FUEL_BURN_kg",
            "CRUISE_1H_FUEL_BURN_kg",
            "DESCENT_FUEL_BURN_kg",
            "TOTAL_MISSION_FUEL_BURN_kg",
        ]:
            if row in mission_fuel_burn_df.index:
                combined_rows[row] = mission_fuel_burn_df.loc[row]

    if mission_emissions_kg_df is not None:
        for row in [
            "LTO_NOx_kg", "LTO_CO_kg", "LTO_HC_kg",
            "CLIMB_NOx_kg", "CLIMB_CO_kg", "CLIMB_HC_kg",
            "CRUISE_NOx_kg", "CRUISE_CO_kg", "CRUISE_HC_kg",
            "DESCENT_NOx_kg", "DESCENT_CO_kg", "DESCENT_HC_kg",
            "TOTAL_MISSION_NOx_kg", "TOTAL_MISSION_CO_kg", "TOTAL_MISSION_HC_kg",
        ]:
            if row in mission_emissions_kg_df.index:
                combined_rows[row] = mission_emissions_kg_df.loc[row]

    return pd.DataFrame(combined_rows).T


def build_and_print_combined_summary_by_bpr(
    fuel_burn_percent_df: pd.DataFrame,
    emissions_percent_df: pd.DataFrame,
    emissions_kg_df: Optional[pd.DataFrame] = None,
    mission_fuel_burn_df: Optional[pd.DataFrame] = None,
    mission_emissions_kg_df: Optional[pd.DataFrame] = None,
    icao_data: Optional[Dict[str, dict]] = None,
    engine_diameter_m: Optional[Dict[str, float]] = None,
    engine_cycle_defaults: Optional[Dict[str, dict]] = None,
    engine_metadata_df: Optional[pd.DataFrame] = None,
    engines_per_table: int = 8,
    title_prefix: str = "COMBINED LTO SUMMARY",
    metadata_decimals: int = 3,
) -> pd.DataFrame:
    combined_df = build_combined_lto_summary_df(
        fuel_burn_percent_df=fuel_burn_percent_df,
        emissions_percent_df=emissions_percent_df,
        emissions_kg_df=emissions_kg_df,
        mission_fuel_burn_df=mission_fuel_burn_df,
        mission_emissions_kg_df=mission_emissions_kg_df,
    )

    if combined_df.empty:
        print("No combined summary to display.")
        return combined_df

    if engine_metadata_df is None:
        engine_metadata_df = build_engine_metadata_from_sources(
            engine_names=list(combined_df.columns),
            icao_data=icao_data,
            engine_diameter_m=engine_diameter_m,
            engine_cycle_defaults=engine_cycle_defaults,
        )

    bpr_row = engine_metadata_df.loc["BPR"] if "BPR" in engine_metadata_df.index else pd.Series(index=combined_df.columns, dtype=float)

    band_map: Dict[str, List[str]] = {}
    for col in combined_df.columns:
        label = _bpr_band_label(bpr_row.get(col))
        band_map.setdefault(label, []).append(col)

    ordered_bands = [
        "BPR < 2",
        "2 <= BPR < 4",
        "4 <= BPR < 6",
        "6 <= BPR < 8",
        "8 <= BPR < 10",
        "BPR >= 10",
        "BPR UNKNOWN",
    ]

    for band in ordered_bands:
        cols = band_map.get(band, [])
        if not cols:
            continue

        cols = sorted(cols, key=lambda c: (float("inf") if pd.isna(bpr_row.get(c)) else bpr_row.get(c), c))
        chunks = chunk_list(cols, engines_per_table)

        for i, subcols in enumerate(chunks, start=1):
            sub_meta = engine_metadata_df.reindex(columns=subcols)
            sub_results = combined_df[subcols]
            printable = pd.concat([sub_meta, sub_results], axis=0)

            print("\n")
            print("=" * 120)
            print(f"{title_prefix} — {band} — TABLE {i}/{len(chunks)}")
            print("=" * 120)
            _print_mixed_table(
                printable,
                meta_labels=list(sub_meta.index),
                percent_rows=DEFAULT_PERCENT_ROWS,
                kg_rows=DEFAULT_KG_ROWS,
                metadata_decimals=metadata_decimals,
            )

    return combined_df
