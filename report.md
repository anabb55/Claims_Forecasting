No missing values were found across any column. This is expected because the dataset appears to be curated and insurance attributes are typically mandatory.



Claim counts are highly zero-inflated (median = 0, mean ≈ 0.05), with a long right tail (max = 16 claims).



Exposure is concentrated around 1–2 years, confirming yearly contracts and renewals. Very small exposure values (< 0.05) exist and lead to artificially high claim frequencies.



Density and BonusMalus show the strongest tail behavior, which is natural: large cities and high-risk drivers create heavy right tails.



Outliers are present but meaningful and should not be removed; insurance risk data is naturally skewed and heavy-tailed.



a small number of risky policies cause many claims



a large number of safe policies cause none



Do not remove very high values for ClaimNb because it is really meaningful and that's what insurance companies are looking for.



very low exposures -> Exposure = 0.03 years



ClaimNb = 1



That implies they had a claim very quickly after the policy started → a high-risk profile.



**zero inflation**



**right skewness**



**variance vs mean**



**over-dispersion**



**why outliers should not be removed**



**why exposure matters**







**Visualizations:**



Claim frequency is highly concentrated near zero, with a long right tail caused by policies with very short exposure periods. This pattern is typical for motor insurance data and is handled naturally by GLMs through the use of an exposure offset.



**Boxplot of ClaimFreq by ClaimNb group**

**Insight 1** — Huge variability even within 1 claim



The ClaimNb = 1 group shows frequencies from:



~1 (full-year exposure)



up to >100 (exposure ≈ 0.01 → “accident right after purchase”)



This demonstrates that **Exposure is a major driver of ClaimFreq variability.**







**Insight 2** — Multi-claim policies show more stable frequency ranges



For ClaimNb = 3, 4, 5:



the boxes are narrower



frequencies are typically higher (means > 5 or > 10)







**Insight 3** — Extreme values occur in 1-claim and 2-claim policies



This is counterintuitive but typical:



Why?



Because high frequencies usually come from:



👉 short exposure periods

not from many claims.



exposure variability matters less (more claims overwhelm the denominator)





**Exposure -distribution**



A dominant peak occurs at exactly 1 year, reflecting standard annual contract terms. The broad mass of exposure values between 0 and 1 year corresponds to policies issued mid-year, cancellations, or customers who left early; these short-duration policies later explain the high-frequency outliers. A smaller right tail beyond 1 year indicates renewed policies and multi-year customers, which are naturally less frequent.



Area grouped by mean ClaimFreq

The most risky area is F.

Veh Brand grouped by mean ClaimFreq

B12 is brand with the highest rate of claim freq.





VehGas grouped by mean ClaimFreq

Regular cars have drastically higher claim frequency. Diesel cars have just a few claims.

Region grouped by mean ClaimFreq
R21 - most





Correlation between target and numerical values

binning:

Grouped analysis of key numerical variables reveals several meaningful risk patterns. Claim frequency is highest among young drivers and decreases sharply for middle-aged drivers. Vehicle age shows a mild increase in risk up to around 10 years, followed by a decline for older vehicles. Higher-power vehicles exhibit elevated risk, while the Bonus–Malus variable shows the strongest relationship: high-malus drivers have drastically higher and more volatile claim frequencies. Overall, the grouped trends indicate that driver characteristics and historical behaviour are strong predictors of future claims.



Two-claim events:
Two-claim events are extremely rare but highly informative.

They occur almost exclusively among policies with long exposure periods, confirming that higher observation time naturally increases the chance of multiple claims. When normalized by exposure, the claim frequency for the 2+ claim group is several times higher than for 0- or 1-claim customers, highlighting a small but high-risk subsegment of the portfolio.





Because policies have different exposure times, I performed most exploratory analysis on claim frequency (ClaimNb / Exposure), which normalizes claims to a per-year rate. For modeling, I predict the number of claims (ClaimNb) while incorporating Exposure as an offset/sample weight so that longer policies have proportionally more influence







**Models**



Instead of predicting raw claim counts directly, I modeled claim frequency (claims per year) and used Exposure as a weight to properly scale each observation.

This ensures that:



policies active for a short time do not distort the model



long-running policies contribute proportionally to the model











Error Analysis \& Model Refinements



The top 10 largest residuals all correspond to policies with extremely short exposure periods (e.g., 0.0027 or 0.01 years, which represent only a few days of coverage) but at least one reported claim. Because ClaimFreq is defined as ClaimNb / Exposure, even a single claim in such a short period produces very large annualized frequencies (e.g., 1 claim in 0.0027 years → ClaimFreq ≈ 366). These cases are statistical outliers and are poorly represented in the training data, so the model—which typically predicts reasonable frequencies (0.05–1.0)—cannot capture these extreme values. The largest residuals therefore reflect data extremes rather than systematic model errors.



To address this, several refinements could be considered:

(1) treating very short-exposure policies separately or excluding them from the main model,

(2) capping or winsorizing extreme ClaimFreq values,



