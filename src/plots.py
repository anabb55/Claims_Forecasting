import matplotlib.pyplot as plt
import seaborn as sns
from data_prep import load_data, add_claim_freq
import pandas as pd
import numpy as np

df = load_data("data/freMTPL2freq.csv")
df = add_claim_freq(df)

# ClaimNb - distribution
plt.figure(figsize=(10, 6))
sns.countplot(x = "ClaimNb", data = df)
plt.title("Distribution of Claim Counts")
plt.xlabel("Number of Claims during Exposure Period")
plt.ylabel("Number of Policies")
plt.yscale("log")
plt.show()


## ClaimFreq - frequency per exposure
## majority of policies have frequency very close to zero. Although a few customers have very high frequencies, these are rare and result from short-duration contracts where a single claim inflates the ratio
df["ClaimFreq_plot"] = df["ClaimFreq"].clip(upper=df["ClaimFreq"].quantile(0.99))
plt.figure(figsize=(10, 8))
sns.histplot(df["ClaimFreq_plot"], bins = 30)
plt.xscale("log")
plt.title("Distribution of Claim Frequency")
plt.xlabel("Claim Frequency (ClaimNb / Exposure)")
plt.ylabel("Number of Policies")
plt.show()


##Boxplot of ClaimFreq by ClaimNb group
##The boxplot of claim frequency grouped by the number of claims shows the effect of exposure on the frequency metric.
plt.figure(figsize=(10,8))
sns.boxplot(x="ClaimNb", y="ClaimFreq", data=df[df["ClaimFreq"] > 0])
plt.yscale("log")
plt.title("Claim Frequency by Claim Count (non-zero)")
plt.show()

##Exposure distribution
plt.figure(figsize = (10, 8))
sns.histplot(df["Exposure"], bins = 30, kde = True)
plt.title("Distribution of Exposure")
plt.xlabel("Exposure in years")
plt.ylabel("Number of Policies")
plt.yscale("log")
plt.show()


fig, axes = plt.subplots(2, 2, figsize=(12, 8))

sns.histplot(df["DrivAge"], bins=30, ax=axes[0, 0])
axes[0, 0].set_title("Driver Age")

sns.histplot(df["VehAge"], bins=30, ax=axes[0, 1])
axes[0, 1].set_title("Vehicle Age")

sns.histplot(df["BonusMalus"], bins=30, ax=axes[1, 0])
axes[1, 0].set_title("BonusMalus")

sns.histplot(df["Density"], bins=30, ax=axes[1, 1])
axes[1, 1].set_title("Population Density")

for ax in axes.flat:
    ax.set_ylabel("Number of Policies")
plt.tight_layout()
plt.show()


##target(claimFreq) and grouped categorical values
cat_cols = ["Area", "VehBrand", "VehGas", "Region"]
for col in cat_cols:
    plt.figure(figsize=(10, 8))
    df_grouped = df.groupby(col)["ClaimFreq"].mean().sort_values()
    sns.barplot(x = df_grouped.index, y = df_grouped.values)
    plt.title(f"Average Claim Frequency by {col}")
    plt.ylabel("Mean Claim Frequency")
    plt.yscale("log")
    plt.show()


##target and other numerical values

df["DrivAge_bin"] = pd.cut(df["DrivAge"], bins = [18, 25, 35, 45, 60, 100])
df["VehAge_bin"] = pd.cut(df["VehAge"], bins = [0, 3, 7, 12, 20, 120])
df["VehPower_bin"] =  pd.cut(df["VehPower"], bins = [4, 6, 9, 12, 20])
df["BonusMalus_bin"] = pd.cut(df["BonusMalus"], bins = [50, 100, 150, 200, 250, 350])
df["Density_bin"] = pd.qcut(df["Density"], q = 10)
for col in ["DrivAge_bin", "VehAge_bin", "VehPower_bin", "BonusMalus_bin", "Density_bin"]:
    plt.figure(figsize=(10, 8))
    sns.pointplot(x = col, y = "ClaimFreq", data=df, estimator = np.mean, color="pink")
    plt.title(f"Mean Claim Frequency by {col}")
    plt.yscale("log")
    plt.show()

##heatmap - not that helpful because ClaimNb is mostly 0
numeric_cols = ["VehPower", "VehAge", "DrivAge", "BonusMalus", "Density", "ClaimFreq", "ClaimNb", "Exposure"]
corr = df[numeric_cols].corr(method="spearman")
plt.figure(figsize=(12, 8))
sns.heatmap(corr, annot = True, cmap = "coolwarm", fmt = ".2f")
plt.title("Correlation Heatmap of Numerical Features")
plt.show()

##Frequency of 0, 1, 2+ claims
df["ClaimGroup"] = df["ClaimNb"].apply(lambda x: x if x<2 else 2)

sns.countplot(data=df, x="ClaimGroup")
plt.yscale("log")
plt.title("Distribution: 0 vs 1 vs 2+ claims")
plt.show()

##Exposure vs ClaimGroup
sns.boxplot(data=df, x="ClaimGroup", y="Exposure")
plt.yscale("log")
plt.title("Exposure distribution for 0, 1 and 2+ claims")
plt.show()

##ClaimFreq by ClaimGroup
sns.pointplot(data=df, x="ClaimGroup", y="ClaimFreq", estimator=np.mean, ci=None)
plt.yscale("log")
plt.title("Mean Claim Frequency for 0, 1 and 2+ claims")
plt.show()

##BonusMalus vs ClaimGroup
plt.figure(figsize=(10, 8))
sns.boxplot(data=df, x="ClaimGroup", y="BonusMalus")
plt.title("Bonus-Malus Distribution across Claim Counts (0, 1, 2+)")
plt.xlabel("Claim Count Group")
plt.ylabel("Bonus-Malus")
plt.show()



