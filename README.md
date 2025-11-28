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

## 2. Visualizations and Variable Behavior

This section uses a set of univariate and group-based visualizations to understand how the main variables behave and how they relate to the target ClaimFreq, with special attention to Exposure.

### 2.1 Univariate Distributions

Several plots were created to inspect marginal distributions:

* **ClaimNb**: a countplot (on a log y-scale) confirms that the vast majority of policies have zero claims, with a rapidly decreasing count for 1, 2, … up to the maximum of 16 claims.
  <img width="955" height="577" alt="image" src="https://github.com/user-attachments/assets/14e9b34c-3da6-4899-aa87-8d9597c362bd" />

* **ClaimFreq**: a histogram of a capped version of ClaimFreq (top 1% clipped, log x-scale) shows that most policies have frequencies extremely close to zero, while very high frequencies are rare and mainly driven by short exposures with at least one claim.


 * **ClaimFreq by ClaimNb (boxplot)**: a boxplot of claim frequency grouped by claim count (restricted to non-zero values) shows that, for the same number of claims, shorter exposure periods lead to much higher annualized frequencies, resulting in wide variability within each claim group.

* **Exposure**: a histogram (log y-scale) shows that most policies have exposure around 1 year, with additional mass at 2 years (renewals) and a small share of very short or slightly longer contracts.
* **Numeric features (`DrivAge`, `VehAge`, `BonusMalus`, `Density`)**: histograms highlight realistic age ranges, a wide spread of Bonus-Malus values, and a strongly skewed distribution for population density.

These plots confirm that the data is highly skewed and that log scales are helpful for visual interpretation.

### 2.2 Target vs. Categorical Features

To explore how claim frequency varies across categories, bar plots of **mean `ClaimFreq`** were produced for:

* `Area`
* `VehBrand`
* `VehGas`
* `Region`

For each feature, the dataset is grouped by the category and the average `ClaimFreq` is plotted (often on a log scale). This reveals:

* systematic differences in risk between regions and areas,
* distinct patterns across vehicle brands,
* noticeable differences between fuel types (Regular vs Diesel).

These group comparisons provide a first view of which categorical segments carry higher average risk.

### 2.3 Target vs. Binned Numeric Features

To better understand nonlinear relationships, key numeric variables were binned and compared to `ClaimFreq`:

* `DrivAge` binned into age groups (e.g., 18–25, 25–35, …)
* `VehAge` binned into age bands
* `VehPower` binned into power ranges
* `BonusMalus` binned into score ranges
* `Density` split into deciles

For each binned feature, a point plot of **mean `ClaimFreq`** is shown (log scale on the y-axis). This highlights, for example:

* increased claim frequency for certain driver age groups,
* higher risk for specific vehicle ages and power ranges,
* a clear relationship between Bonus-Malus segments and observed frequency,
* differences in frequency across density deciles.

### 2.4 Correlations Between Numeric Variables

A Spearman correlation heatmap was produced for the main numeric variables (`VehPower`, `VehAge`, `DrivAge`, `BonusMalus`, `Density`, `ClaimFreq`, `ClaimNb`, `Exposure`). While correlations are generally moderate, the heatmap helps confirm:

* expected relationships between `ClaimNb` and `ClaimFreq`,
* limited linear correlation between most features and the target, supporting the use of nonlinear models such as XGBoost.

### 2.5 Key Interactions: 0 vs 1 vs 2+ Claims

To explicitly highlight multi-claim behavior, a derived variable `ClaimGroup` was created:

* `0` = no claims
* `1` = exactly one claim
* `2` = two or more claims (2+)

Several visualizations were then used:

* a countplot of `ClaimGroup` (log scale) to show how rare 2+ claim events are,
* a boxplot of `Exposure` by `ClaimGroup` to compare policy durations for 0, 1, and 2+ claim groups,
* a point plot of mean `ClaimFreq` by `ClaimGroup`, illustrating how frequency grows sharply for the 2+ segment,
* a boxplot of `BonusMalus` by `ClaimGroup`, showing that policies with more claims are associated with worse Bonus-Malus scores.

These plots explicitly capture the interaction between claim counts, exposure, and past driving behavior, and they motivate the later modeling choices and error analysis.







