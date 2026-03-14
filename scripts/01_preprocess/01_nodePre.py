"""
01_nodePre.py

Preprocess original SWOT L2 HR RiverSP node data.

This script extracts selected variables from the original
SWOT_L2_HR_RiverSP_Node shapefile archives and converts them
into daily CSV files for further analysis.

Input
-----
Original SWOT RiverSP Node data downloaded from NASA Earthdata:
data/raw/RiverSP_VC/
    SWOT_L2_HR_RiverSP_Node_*.zip

Output
------
Daily node datasets:
data/derived_raw/RiverSP_VC_daily/
    node_YYYYMMDD.csv

Notes
-----
The generated daily CSV files are intermediate datasets derived
from the original RiverSP products. Due to their large size,
they are not included in the repository but can be regenerated
using this script.

Part of the preprocessing workflow for the SWOT RiverSP
obstruction analysis project.
"""

from pathlib import Path
from glob import glob
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import fiona


# Project root: SWOT_RiverSP_Obstruction/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Default input/output directories
BASE_DIR = PROJECT_ROOT / "data" / "raw" / "RiverSP_VC" # SWOT_L2_HR_RiverSP data downloaded from Earthdata
OUTPUT_DIR = PROJECT_ROOT / "data" / "derived_raw" / "RiverSP_VC_daily"

# Date range to process
DATES = pd.date_range(start="2023-07-26", end="2025-05-03")
DATE_STRINGS = DATES.strftime("%Y%m%d").tolist()

# Fields to keep from the shapefile
FIELDS_TO_KEEP = [
    "node_id",
    "time",
    "wse",
    "wse_u",
    "width",
    "ice_clim_f",
    "dark_frac",
    "rdr_sig0",
    "node_q_b",
    "geometry"
]


def process_zip_file(zip_path: str, temp_extract_root: Path) -> pd.DataFrame | None:
    """
    Process a single ZIP file:
    1. Extract the shapefile
    2. Read selected fields with Fiona
    3. Filter invalid records (time <= -1)
    4. Return a pandas DataFrame

    Parameters
    ----------
    zip_path : str
        Path to the ZIP file.
    temp_extract_root : Path
        Directory used for temporary extraction.

    Returns
    -------
    pd.DataFrame | None
        DataFrame containing selected records, or None if no valid data.
    """
    zip_path = Path(zip_path)
    extract_dir = temp_extract_root / zip_path.stem
    shp_file = extract_dir / f"{zip_path.stem}.shp"

    try:
        # Extract archive
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        if not shp_file.exists():
            print(f"Shapefile not found: {shp_file}")
            shutil.rmtree(extract_dir, ignore_errors=True)
            return None

        records = []
        with fiona.open(shp_file, "r") as src:
            for feature in src:
                properties = {
                    field: feature["properties"].get(field)
                    for field in FIELDS_TO_KEEP
                }

                # Keep only valid time records
                if properties["time"] is not None and properties["time"] > -1:
                    records.append(properties)

        shutil.rmtree(extract_dir, ignore_errors=True)

        if not records:
            return None

        return pd.DataFrame.from_records(records, columns=FIELDS_TO_KEEP)

    except Exception as e:
        print(f"Error processing file {zip_path}: {e}")
        shutil.rmtree(extract_dir, ignore_errors=True)
        return None


def process_date(
    date_str: str,
    base_dir: Path,
    output_dir: Path,
    num_threads: int = 8,
) -> None:
    """
    Process all RiverSP node ZIP files for a given date and save them as one CSV.

    Parameters
    ----------
    date_str : str
        Date string in YYYYMMDD format.
    base_dir : Path
        Directory containing raw RiverSP ZIP files.
    output_dir : Path
        Directory for output CSV files.
    num_threads : int, optional
        Number of threads for parallel processing.
    """
    pattern = str(base_dir / f"SWOT_L2_HR_RiverSP_Node_*_{date_str}*.zip")
    zip_files = glob(pattern)

    if not zip_files:
        print(f"No files found for date {date_str}")
        return

    print(f"Processing {len(zip_files)} files for date {date_str}...")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(
            process_zip_file,
            zip_files,
            [base_dir] * len(zip_files),
        )
        dfs = [df for df in results if df is not None]

    if not dfs:
        print(f"No valid data for date {date_str}")
        return

    merged_df = pd.concat(dfs, ignore_index=True)
    output_file = output_dir / f"node_{date_str}.csv"
    merged_df.to_csv(output_file, index=False)

    print(f"Finished processing date {date_str}")
    print(f"Saved to: {output_file}")
    print(f"Current time: {datetime.now().strftime('%H:%M:%S')}")


def main() -> None:
    """Run daily preprocessing for all dates in the configured range."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for date_str in DATE_STRINGS:
        process_date(
            date_str=date_str,
            base_dir=BASE_DIR,
            output_dir=OUTPUT_DIR,
            num_threads=48,
        )


if __name__ == "__main__":
    main()