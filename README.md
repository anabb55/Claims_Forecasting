# Car Insurance Claim Frequency Modeling

This project forecasts the **number of car-insurance claims per policy period** by modeling **claim frequency** (`ClaimFreq = ClaimNb / Exposure`) using both **GLM-type models (Poisson / Tweedie)** and a **tree-based XGBoost model**.  
The goal is not only to achieve good predictive performance, but also to provide **business-relevant insights** and **actionable recommendations**.

---

## 1. Data Preparation and Exploration

The dataset is loaded, cleaned, and enriched using the following steps:

- `load_data` – reads the raw CSV file.  
- `basic_clean` – handles type conversions, sanity checks, and removal of invalid records.  
- `add_claim_freq` – computes the target variable:  
  **`ClaimFreq = ClaimNb / Exposure`**.

The modeling dataset includes:

- **Features**: `Area`, `VehBrand`, `VehGas`, `Region`, `VehPower`, `VehAge`, `DrivAge`, `BonusMalus`, `Density`
- **Target**: `ClaimFreq`
- **Sample weight**: `Exposure` 

---
