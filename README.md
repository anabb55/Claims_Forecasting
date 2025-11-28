# Car Insurance Claim Frequency Modeling

This project forecasts the **number of car-insurance claims per policy period** by modeling **claim frequency** (`ClaimFreq = ClaimNb / Exposure`) using both **GLM-type models (Poisson / Tweedie)** and a **tree-based XGBoost model**.  
The goal is not only to achieve good predictive performance, but also to provide **business-relevant insights** and **actionable recommendations**.

---

## 1. Data Preparation and Exploration

The dataset is loaded, cleaned, and enriched using the following steps:

- load_data – reads the raw CSV file.  
- basic_clean – handles type conversions, sanity checks, and removal of invalid records.  
- add_claim_freq – computes the target variable:  
  **ClaimFreq = ClaimNb / Exposure**.

The modeling dataset includes:

- **Features**: `Area`, `VehBrand`, `VehGas`, `Region`, `VehPower`, `VehAge`, `DrivAge`, `BonusMalus`, `Density`
- **Target**: `ClaimFreq`
- **Sample weight**: `Exposure` 

---

### Numeric Profiling

A detailed statistical summary was generated for all numeric fields (mean, standard deviation, min/max, and key percentiles). This step helps identify skewness, outliers, and the overall distribution of key variables.

<img width="803" height="170" alt="image" src="https://github.com/user-attachments/assets/2dd8e503-ccf9-4efd-8bad-ea4b66c9c141" />


Key observations:

* ClaimNb is extremely zero-inflated, with only a small proportion of policies having one or more claims.
* Exposure is centered around one year but includes very short durations.
* VehAge, DrivAge, and BonusMalus span wide but reasonable value ranges.
* Density shows a heavy right tail, reflecting strong differences between rural and urban regions.

---

### Handling Missing Values and Data Quality

* The dataset was checked for missing values across all features.
* Rows with invalid or inconsistent values (e.g., negative exposure) were removed.
* Categorical variables were verified to ensure consistent encoding before modeling.

---

### Exposure Considerations

Exposure represents the length of time (in years) that a policy was active:

* Standard contracts appear as Exposure ≈ 1.0
* Renewals show Exposure = 2.0
* Very short periods (e.g., < 0.1) typically indicate early cancellation or short-term coverage

Because ClaimFreq divides by Exposure, extremely small exposure values combined with at least one claim produce very large frequency values. These observations influence model training and require special attention during error analysis.

---

### Outlier Detection

An IQR-based approach was used to identify potential outliers in numeric variables. The summary shows that:

* ClaimNb and VehPower each have around 5% flagged observations.
* BonusMalus has roughly 9% outliers, reflecting variation in past driving behavior.
* Density shows the highest proportion of potential outliers (≈11%), consistent with large differences between rural and urban areas.
* No outliers were detected for Exposure, which behaves as expected under contractual rules.

Outliers were kept in the dataset because many represent real high-risk situations.

<img width="385" height="152" alt="image" src="https://github.com/user-attachments/assets/c39d1ad9-ce45-4a41-9e93-b7e3cd91260b" />


---






