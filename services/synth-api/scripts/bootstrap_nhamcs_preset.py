from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

import pandas as pd
from pandas.io.stata import StataReader


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
PRESETS_DIR = WORKSPACE_ROOT / "data" / "presets"
PRESET_ID = "nhamcs_ed_2022_curated"
OUTPUT_CSV = PRESETS_DIR / f"{PRESET_ID}.csv"
OUTPUT_METADATA = PRESETS_DIR / f"{PRESET_ID}.metadata.json"

DATA_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/stata/ed2022-stata.zip"
DOC_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/doc22-ed-508.pdf"
README_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/readme2022.txt"


def clean_label(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.replace("...", "").replace("  ", " ")


def remap(series: pd.Series, mapping: dict[object, str], negative_to_none: bool = True) -> pd.Series:
    cleaned_mapping = {key: clean_label(value) for key, value in mapping.items()}
    values = series.map(cleaned_mapping)
    values = values.replace(
        {
            "Blank": None,
            "All sources of payment are blank": "Unknown",
            "Unknown (data not available)": "Unknown",
            "Not Applicable": "Not applicable",
        }
    )
    if negative_to_none:
        return values.where(~series.fillna(0).astype(float).lt(0), None)
    return values


def parse_arrival_hour(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    hours = (numeric // 100).where(numeric >= 0, None)
    return hours.clip(lower=0, upper=23)


def build_dataset(dataframe: pd.DataFrame, labels: dict[str, dict[object, str]]) -> pd.DataFrame:
    yes_no_2 = {-9: None, -8: "Unknown", 1: "Yes", 2: "No"}
    yes_no_1 = {-9: None, -8: "Unknown", -7: None, 0: "No", 1: "Yes"}
    transfer_map = {-9: None, -8: "Unknown", -7: "Not applicable", 1: "Yes", 2: "No"}

    curated = pd.DataFrame(
        {
            "visit_month": remap(dataframe["VMONTH"], labels["VMONTHF"], negative_to_none=False),
            "visit_day_of_week": remap(dataframe["VDAYR"], labels["VDAYRF"], negative_to_none=False),
            "arrival_hour": parse_arrival_hour(dataframe["ARRTIME"]),
            "wait_time_minutes": pd.to_numeric(dataframe["WAITTIME"], errors="coerce").where(dataframe["WAITTIME"] >= 0),
            "length_of_visit_minutes": pd.to_numeric(dataframe["LOV"], errors="coerce").where(dataframe["LOV"] >= 0),
            "age_years": pd.to_numeric(dataframe["AGE"], errors="coerce").where(dataframe["AGE"] >= 0),
            "sex": remap(dataframe["SEX"], labels["SEXF"], negative_to_none=False),
            "race_ethnicity": remap(dataframe["RACERETH"], labels["RACERETHF"], negative_to_none=False),
            "arrived_by_ambulance": dataframe["ARREMS"].map(yes_no_2),
            "transfer_in": dataframe["AMBTRANSFER"].map(transfer_map),
            "triage_level": remap(dataframe["IMMEDR"], labels["IMMEDRF"], negative_to_none=False),
            "pain_scale": pd.to_numeric(dataframe["PAINSCALE"], errors="coerce").where(dataframe["PAINSCALE"] >= 0),
            "chronic_conditions_count": pd.to_numeric(dataframe["TOTCHRON"], errors="coerce").where(dataframe["TOTCHRON"] >= 0),
            "primary_reason": remap(dataframe["RFV13D"], labels["RFV3DF"], negative_to_none=False),
            "primary_payer": remap(dataframe["PAYTYPER"], labels["PAYTYPERF"], negative_to_none=False),
            "admitted_inpatient": dataframe["ADMITHOS"].map(yes_no_1),
            "admit_unit": remap(dataframe["ADMIT"], labels["ADMITF"], negative_to_none=False),
            "observation_minutes": pd.to_numeric(dataframe["OBSSTAY"], errors="coerce").where(dataframe["OBSSTAY"] >= 0).fillna(0),
            "left_against_advice": dataframe["LEFTAMA"].map({0: "No", 1: "Yes"}),
            "discharge_disposition": remap(dataframe["ADISP"], labels["ADISPF"], negative_to_none=False),
        }
    )

    curated["observation_minutes"] = curated["observation_minutes"].round(0)

    def classify_outcome(row: pd.Series) -> str:
        if row["left_against_advice"] == "Yes":
            return "Left before completion"
        if row["admitted_inpatient"] == "Yes":
            return "Inpatient admission"
        if row["observation_minutes"] and row["observation_minutes"] > 0:
            return "Observation pathway"
        disposition = (row["discharge_disposition"] or "").lower()
        if "transfer" in disposition or "facility" in disposition:
            return "Transfer / facility handoff"
        return "Home or community resolution"

    curated["visit_outcome"] = curated.apply(classify_outcome, axis=1)
    curated = curated.dropna(subset=["arrival_hour", "wait_time_minutes", "length_of_visit_minutes", "age_years"])
    curated = curated.fillna(
        {
            "triage_level": "Unknown",
            "primary_reason": "Unknown",
            "primary_payer": "Unknown",
            "discharge_disposition": "Unknown",
            "admit_unit": "Not admitted",
            "sex": "Unknown",
            "race_ethnicity": "Unknown",
            "arrived_by_ambulance": "Unknown",
            "transfer_in": "Unknown",
            "left_against_advice": "No",
        }
    )
    curated["arrival_hour"] = curated["arrival_hour"].astype(int)
    curated["wait_time_minutes"] = curated["wait_time_minutes"].clip(lower=0).round(0).astype(int)
    curated["length_of_visit_minutes"] = curated["length_of_visit_minutes"].clip(lower=1).round(0).astype(int)
    curated["age_years"] = curated["age_years"].clip(lower=0).round(0).astype(int)
    curated["pain_scale"] = curated["pain_scale"].clip(lower=0, upper=10).round(0)
    curated["chronic_conditions_count"] = curated["chronic_conditions_count"].clip(lower=0).round(0)
    curated["observation_minutes"] = curated["observation_minutes"].clip(lower=0).round(0).astype(int)

    return curated


def main() -> None:
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="nhamcs_"))
    try:
        zip_path = temp_dir / "ed2022-stata.zip"
        import urllib.request

        urllib.request.urlretrieve(DATA_URL, zip_path)
        with ZipFile(zip_path) as archive:
            archive.extractall(temp_dir)

        dta_path = temp_dir / "ed2022-stata.dta"
        reader = StataReader(dta_path)
        labels = reader.value_labels()
        dataframe = reader.read(convert_categoricals=False)

        curated = build_dataset(dataframe, labels)
        curated.to_csv(OUTPUT_CSV, index=False)

        metadata = {
            "id": PRESET_ID,
            "name": "NHAMCS 2022 ED Operations Preset",
            "source_name": "CDC/NCHS NHAMCS 2022 Emergency Department Public-Use File",
            "source_url": DATA_URL,
            "documentation_url": DOC_URL,
            "notes": (
                "Curated operational subset derived from the 2022 NHAMCS emergency department public-use file. "
                "Use for demo synthesis only and preserve NCHS statistical-use cautions."
            ),
            "columns": curated.columns.tolist(),
            "row_count": int(len(curated)),
            "readme_url": README_URL,
        }
        OUTPUT_METADATA.write_text(json.dumps(metadata, indent=2))

        print(f"Wrote {len(curated)} rows to {OUTPUT_CSV}")
        print(f"Wrote metadata to {OUTPUT_METADATA}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
