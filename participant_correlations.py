import pandas as pd
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

participant_data = pd.read_csv("participant_stats.csv")

dyslexic_data = participant_data[participant_data["dyslexia"] == 'yes']

var1 = 'comprehension_accuracy'
var2 = 'words_per_minute'
var3 = 'score_reading_comprehension_test'
var4 = 'pseudohomophone_score'

rho, pval =stats.spearmanr(dyslexic_data[var1], dyslexic_data[var3])
print(rho, pval)
significant = "*" if pval<0.05 else ""

sns.regplot(data = dyslexic_data, x=var1, y=var3, color="g",ci=68, truncate=False)

plt.title("dyslexic readers, ρ="+"{:.2f}".format(rho)+significant)
#plt.xlabel(var1)
plt.savefig("plots/dyslexic-"+var1+"-"+var3)
plt.close()

typical_data = participant_data[participant_data["dyslexia"] == 'no']

var1 = 'comprehension_accuracy'
var2 = 'words_per_minute'

rho, pval =stats.spearmanr(typical_data[var1], typical_data[var2])
print(rho, pval)
significant = "*" if pval<0.05 else ""

sns.regplot(data = typical_data, x=var1, y=var2, color="b",ci=68, truncate=False)

plt.title("typical readers, ρ="+"{:.2f}".format(rho)+significant)
plt.savefig("plots/typical-"+var1+"-"+var2)
