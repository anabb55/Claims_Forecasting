import matplotlib.pyplot as plt
import seaborn as sns
from data_prep import load_data, add_claim_freq

df = load_data("data/freMTPL2freq.csv")
df = add_claim_freq(df)

## ClaimNb - distribution
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

sns.histplot(df["DrivAge"], bins=50, ax=axes[0, 0])
axes[0, 0].set_title("Driver Age")

sns.histplot(df["VehAge"], bins=50, ax=axes[0, 1])
axes[0, 1].set_title("Vehicle Age")

sns.histplot(df["BonusMalus"], bins=50, ax=axes[1, 0])
axes[1, 0].set_title("BonusMalus")

sns.histplot(df["Density"], bins=50, ax=axes[1, 1])
axes[1, 1].set_title("Population Density")

for ax in axes.flat:
    ax.set_ylabel("Number of Policies")

plt.tight_layout()
plt.show()


