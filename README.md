# SWOT_RiverSP_Obstruction
## Overview
This repository is the preprocessing and detection workflow used to identify potential river obstructions from SWOT RiverSP observations.

The workflow processes the original SWOT RiverSP node products and applies a step-change detection algorithm to identify abrupt changes in water surface elevation (WSE) along river reaches. These discontinuities may indicate the presence of hydraulic controls such as dams, weirs, or other anthropogenic or natural obstructions.

## Repository Structure
```text
scripts/
├── 01_preprocess
│   ├── 01_nodePre.py # Extract variables from SWOT RiverSP node shapefile archives
│   └── 02_DataPre.ipynb # Prepare analysis-ready datasets
│
└── 02_detection
    └── 01_SWOOP.ipynb # SWOOP detection workflow
```

## Data File Structure

The workflow uses the following data directory structure:

```text
data/
├── raw/ # Original SWOT data files downloaded from NASA Earthdata
│   └── RiverSP_VC/
│       └── SWOT_L2_HR_RiverSP_Node_*.zip
│
├── derived_raw/ # Intermediate datasets generated from initial preprocessing of raw data
│   ├── RiverSP_VC_daily/
│   │   └── node_YYYYMMDD.csv
│   │
│   ├── continent/
│   │   └── node_{af,eu,si,as,au,sa,na,ar,gr}_noice.csv
│   │
│   ├── continent_filtered/
│   │   └── node_{af,eu,si,as,au,sa,na,ar,gr}_v5.csv
│   │
│   ├── continent_valid_dates/
│   │   └── node_{af,eu,si,as,au,sa,na,ar,gr}_v5.10.csv
│   │
│   ├── node_geometry/
│   │   └── node_geometry.csv
│   │
│   └── gsw_tiles/
│       └── occurrence-*.tif
│
├── input_data/ # Analysis-ready datasets used as inputs for detection algorithms (available in Zenodo)
│   ├── node_train_valid_v5.10.csv
│   ├── node_{af,eu,si,as,au,sa,na,ar,gr}_test_v5.10.csv
│   ├── node_sigma0_v5.10.csv
│   └── node_occu_mean.csv
│
└── results/ # Detection results and annnotated datasets (available in Zenodo)
    ├── train_valid_step_candidates_v6.8.csv
    ├── train_valid_step_candidates_v6.8_ANNOTATED.csv
    ├── {af,eu,si,as,au,sa,na,ar}_test_step_candidates_v6.8.csv
    ├── test_step_candidates_v6.8.csv
    └── global_predicted_v6.8.csv
```
## Requirements

- Python 3.10+
- Required Python packages:
    - numpy>=1.24
    - pandas>=2.0
    - geopandas>=0.14
    - shapely>=2.0
    - fiona>=1.9
    - pyproj>=3.5
    - rasterio>=1.3
    - rioxarray>=0.15
    - dask>=2024.1
    - scikit-learn>=1.8

## Script Descriptions
### 1. Raw data preprocessing (`01_preprocess/01_nodePre.py`)
Preprocesses the original SWOT Level-2 HR **RiverSP node shapefile** archives to **daily node-level CSV files** for further analysis.
### 2. Data preparation (`01_preprocess/02_DataPre.ipynb`)
Prepares **analysis-ready datasets** from the daily node data generated in the previous step.
### 3. Detection algorithm (`02_detection/01_SWOOP.ipynb`)
Implements the **SWOOP (SWOT Obstruction Profile)** workflow.

## Usage
### Data Download
The preprocessing scripts in `scripts/01_preprocess/` require several large public datasets.  
All required datasets are **publicly available and can be downloaded from the original data providers**.
- SWOT RiverSP: https://search.earthdata.nasa.gov/
- GSW: https://global-surface-water.appspot.com/download

The core workflow of detection algorithm in `scripts/02_detection/` requires prepared analysis-ready datasets. To facilitate reproducibility,
these datasets are **publicly available on Zenodo**.
- Input and result datasets: https://zenodo.org/record/XXXXX

### Open and run:  
```scripts/02_detection/01_SWOOP.ipynb```

## Citation
Xu, Y., Lin, P*., Yuan, Z., et al. Global Detection of Riverine Hydraulic Discontinuities from Satellite SWOT (in prep).  
\* Corresponding Author: Peirong Lin (peironglinlin@pku.edu.cn)  
Contacts: Yue XU (xuyue6371@pku.edu.cn)