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


 * **ClaimFreq by ClaimNb (boxplot)**: a boxplot of claim frequency grouped by claim count shows that, for the same number of claims, shorter exposure periods lead to much higher annualized frequencies.
  <img width="962" height="766" alt="image" src="https://github.com/user-attachments/assets/c4ef1503-282d-4457-93b5-60f2fefd8d3d" />

* **Exposure**: a histogram (log y-scale) shows that most policies have exposure around 1 year, with additional mass at 2 years (renewals) and a small share of very short or slightly longer contracts.
* **Numeric features (DrivAge, VehAge, BonusMalus, Density)**: histograms highlight realistic age ranges, a wide spread of Bonus-Malus values, and a strongly skewed distribution for population density.
* <img width="1177" height="783" alt="image" src="https://github.com/user-attachments/assets/e6a371a6-de7e-4ab6-bebb-4fc6dfa309c4" />


These plots confirm that the data is highly skewed and that log scales are helpful for visual interpretation.

### 2.2 Target vs. Categorical Features

To explore how claim frequency varies across categories, bar plots of **mean `ClaimFreq`** were produced for:

* `Area`
* `VehBrand`
* `VehGas`
* `Region`

  <img width="932" height="742" alt="image" src="https://github.com/user-attachments/assets/82a5c637-66a5-41c3-9a7e-de99e714d0c2" />
  <img width="957" height="756" alt="image" src="https://github.com/user-attachments/assets/601f6adc-599a-4370-8a84-fc2e27609f03" />



For each feature, the dataset is grouped by the category and the average ClaimFreq is plotted. This reveals:

* systematic differences in risk between regions and areas, with Area F showing the highest average claim frequency,
* distinct patterns across vehicle brands, with VehBrand B12 standing out as one of the highest-risk categories,
* noticeable differences between fuel types, where Regular-fuel vehicles exhibit significantly higher risk compared to Diesel.

These group comparisons provide a first view of which categorical segments carry higher average risk.

### 2.3 Target vs. Binned Numeric Features

To better understand nonlinear relationships, key numeric variables were binned and compared to ClaimFreq.
<img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/fe24db8e-17d6-47fd-9894-2fd382f419be" />
<img width="945" height="750" alt="image" src="https://github.com/user-attachments/assets/6aa0074a-23e0-4277-aee9-2ac629577611" />
<img width="968" height="753" alt="image" src="https://github.com/user-attachments/assets/c635cb23-7ce4-4862-8643-316051403393" />


For each binned feature, a point plot of **mean `ClaimFreq`** is shown. This highlights, for example:

* increased claim frequency among younger drivers, with the 18–25 age group showing the highest risk,
* higher risk for specific vehicle power ranges, where the 9–12 power group stands out as the riskiest segment, while the 12–20 range contains relatively few vehicles, causing its average risk to fluctuate more due to limited sample size,
* a strong relationship between Bonus-Malus groups and claim frequency, where lower bands show low risk, while higher bands exhibit a sharp increase in average frequency, consistent with worse prior driving behavior
* differences in frequency across density deciles.

### 2.4 Correlations Between Numeric Variables

A Spearman correlation heatmap was generated for the main numeric variables, but its usefulness is limited because ClaimNb is almost always zero. **For this reason, correlation analysis is not an ideal tool for understanding claim behavior, and inspecting specific claim groups provides far more insight.**

The only meaningful relationship observed is a negative correlation between DrivAge and BonusMalus, indicating that younger drivers tend to have worse Bonus-Malus scores.

### 2.5 Key Interactions: 0 vs 1 vs 2+ Claims

To explicitly highlight multi-claim behavior, a derived variable ClaimGroup was created:

* `0` = no claims
* `1` = exactly one claim
* `2` = two or more claims (2+)
* 
<img width="621" height="456" alt="image" src="https://github.com/user-attachments/assets/7cdbd0a9-190e-4f52-a069-2ee9b42d95a8" />
<img width="631" height="462" alt="image" src="https://github.com/user-attachments/assets/53524b77-929f-48aa-b662-364bb2371568" />
<img width="976" height="747" alt="image" src="https://github.com/user-attachments/assets/47a404e6-2142-4f00-bbd1-7eec394f642a" />


Several visualizations were then used:

* a countplot of ClaimGroup to show how rare 2+ claim events are,
* a point plot of mean ClaimFreq by ClaimGroup, illustrating how frequency grows sharply for the 2+ segment,
* a boxplot of BonusMalus by ClaimGroup, showing that policies with more claims are associated with worse Bonus-Malus scores.

Two-claim events are extremely rare but highly informative.

---

## 3. Modeling Algorithms and Hyperparameter Tuning

The modeling stage includes both **GLM-type models** and a **tree-based nonlinear model**. Instead of predicting raw claim counts directly, I modeled claim frequency (claims per year) and used Exposure as a weight to properly scale each observation.

### 3.1 Modeling Approaches

Two GLM models were implemented:

* **Poisson Regression** – a natural choice for modeling count and frequency data with a log link and non-negative predictions.
* **Tweedie Regression** – a flexible GLM suited for insurance data, as it handles zero-inflation and heavy-tailed target distributions more effectively than a standard linear model.

In addition to GLMs, a **tree-based XGBoost model** with a Poisson objective was trained:

* It can capture nonlinear relationships and complex interactions between driver, vehicle, and geographic features.
* It handles mixed data types well when combined with proper preprocessing (one-hot encoding + scaling).
* It is robust to skewed distributions and extreme values, which are common in ClaimFreq due to short exposure periods.

### 3.2 Preprocessing Pipeline

All models use a unified scikit-learn `Pipeline` that combines:

* `OneHotEncoder` for categorical variables,
* `StandardScaler` for numeric variables,
* the selected model (Poisson, Tweedie, or XGBoost) as the final step.

### 3.3 Hyperparameter Tuning Strategy

Hyperparameter tuning was conducted using **GridSearchCV**. Each model was tuned over a focused set of parameters:

* **Poisson Regression**: regularization strength (`alpha`)
* **Tweedie Regression**: `power` and `alpha`
* **XGBoost**: tree depth, learning rate, number of estimators, subsampling, and feature sampling rate

Cross-validation was used throughout:

* **5-fold CV** for Poisson and Tweedie
* **3-fold CV** for XGBoost, chosen to reduce training time on a large dataset

All models were trained using **sample weights = Exposure**.
<img width="1059" height="58" alt="image" src="https://github.com/user-attachments/assets/171677d1-f2ce-4f20-9493-c16e81a75ed2" />

### 3.4 Model Selection

After tuning, all three models were evaluated on a held-out validation set.
The **XGBoost model** achieved the best predictive performance and was therefore selected as the final model.

<img width="239" height="295" alt="image" src="https://github.com/user-attachments/assets/47470705-9570-4a70-8471-c46d24122533" />

It was retrained on the combined **train + validation** sets and evaluated once on the **test** set.

---

## 4. Feature Importance

The figure below shows the ten most important predictors:

<img width="230" height="190" alt="image" src="https://github.com/user-attachments/assets/b2e0996b-ff34-4d77-8f40-bac57ec4c6d8" />

Key insights:

* **VehGas_Regular** – Regular-fuel vehicles show the highest risk. This matches the EDA results, where Regular engines consistently had higher average claim frequency than Diesel.
* **VehAge** – Older vehicles tend to produce more claims, likely due to wear, outdated safety features, or poorer vehicle condition.
* **VehBrand_B12** – This brand group stands out as a high-risk segment, confirming the patterns seen in the grouped bar plots.
* **BonusMalus** – Higher Bonus-Malus scores correspond to worse driving history. Drivers with a poor record naturally show higher claim frequency.
* **VehGas_Diesel** – Diesel appears in the top features, but with a smaller impact than Regular, which aligns with its lower observed risk.
* **VehPower** – More powerful vehicles contribute to higher risk, and the model uses this signal effectively.
* **DrivAge** – Younger drivers have noticeably higher claim frequencies.
* **Regional indicators (R91)** – Location matters, reflecting differences in traffic density, road conditions, and local driving patterns.

### 4.1 Business Interpretation

The importance ranking aligns well with real-world insurance logic:

* **Driver history and behavior** (Bonus-Malus) strongly influence future claims.
* **Vehicle characteristics** (age, power, brand, fuel type) explain a large share of risk variation.
* **Regional factors** capture environmental and traffic-related differences.
* **Fuel type** emerges as a meaningful segment: Regular-fuel vehicles repeatedly show higher risk.
  
---

## 5. Error Analysis and Model Refinements

I reviewed the ten largest residuals to understand where the model performs poorly. All high-error cases follow the same pattern:

* the policy has very short exposure (often only a few days),
* the policy has at least one claim,
* dividing by such a small exposure produces extremely large ClaimFreq values.

The model cannot predict these extreme values well because they are rare and behave differently from normal-year policies. These points act as statistical outliers, not true model mistakes.
<img width="960" height="191" alt="image" src="https://github.com/user-attachments/assets/d81beebe-0d49-42c5-b266-ffd6b2568f2e" />

### Key Observations

* Every large residual appears in rows with **Exposure < 0.01**.
* ClaimFreq becomes extremely high due to the formula, not because the driver is unusually risky.
* The model consistently predicts reasonable values, while the targets are inflated because of the tiny denominator.

### Suggested Refinements

To improve performance and stability, I recommend:

1. Add a flag for short exposure (Exposure < 0.1).
2. Cap extreme ClaimFreq values.
3. Use a separate model for very short-exposure policies.
4. Increase regularization in XGBoost to reduce sensitivity to extreme points.

---

## 6. Business Interpretation and Recommendations

From a business perspective, these extreme errors highlight **short-term or irregular policy behavior**, not true high-risk customers.

### Recommendations

* Review policies with very short exposure to understand why they end so quickly.
* Apply special pricing rules or minimum premiums for short-duration contracts.
* Check whether short-exposure policies connect to churn.














