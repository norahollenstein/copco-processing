import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate correlations between different characteristics of the participants
participant_data = pd.read_csv("participant_stats.csv")

dyslexic_data = participant_data[participant_data["dyslexia"] == 'yes']
print(len(dyslexic_data), " participants with dyslexia.")


var1 = 'comprehension_accuracy'
var2 = 'words_per_minute'
#var3 = 'score_reading_comprehension_test'
#var4 = 'pseudohomophone_score'

rho, pval =stats.spearmanr(dyslexic_data[var1], dyslexic_data[var2])
print(rho, pval)
print()
significant = "*" if pval<0.05 else ""

sns.regplot(data = dyslexic_data, x=var1, y=var2, color="g",ci=68, truncate=False)

plt.title("dyslexic readers, ρ="+"{:.2f}".format(rho)+significant)
#plt.xlabel(var1)
plt.savefig("plots/dyslexic-corr-"+var1+"-"+var2+".pdf")
plt.close()

typical_data = participant_data[participant_data["dyslexia"] == 'no']
typical_data = typical_data[typical_data["native_language"] == 'Danish']
print(len(typical_data), " native participants without dyslexia.")


rho, pval =stats.spearmanr(typical_data[var1], typical_data[var2])
print(rho, pval)
print()
significant = "*" if pval<0.05 else ""

sns.regplot(data = typical_data, x=var1, y=var2, color="b",ci=68, truncate=False)

plt.title("typical readers, ρ="+"{:.2f}".format(rho)+significant)
plt.savefig("plots/typical-corr-"+var1+"-"+var2+".pdf")
plt.close()

nonnative_data = participant_data[participant_data["native_language"] != 'Danish']
print(len(nonnative_data), " non-native participants.")

rho, pval =stats.spearmanr(nonnative_data[var1], nonnative_data[var2])
print(rho, pval)
print()
significant = "*" if pval<0.05 else ""

sns.regplot(data = nonnative_data, x=var1, y=var2, color="r",ci=68, truncate=False)

plt.title("non-native readers, ρ="+"{:.2f}".format(rho)+significant)
plt.savefig("plots/non_native-corr-"+var1+"-"+var2+".pdf")
