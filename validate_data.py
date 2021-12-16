import pandas as pd
import numpy as np
import math
import collections
import matplotlib.pyplot as plt
import os

#test word length effect
#test word frequency effect
#test omission rate/skipping

word_lengths_ffd = {}
word_lengths_tft = {}
word_lengths_skip = {}

for file in os.listdir('test_reports/'):
    print(file)
    et_data = pd.read_csv('test_reports/'+file)
    # remove practice trials
    et_data = et_data.drop(et_data[et_data.speechId == 1327].index)
    print(len(et_data))
    # remove beginning of speech trials
    et_data = et_data.drop(et_data[et_data.paragraphId == -1].index)
    print(len(et_data))
    print(et_data.columns)


    skipped = 0
    for index, word in et_data.iterrows():
        word_len = len(word.word)
        if not math.isnan(word.word_first_fixation_duration):
            if word_len not in word_lengths_ffd:
                word_lengths_ffd[word_len] = [word.word_first_fixation_duration]
                word_lengths_tft[word_len] = [word.word_total_fix_time]
                word_lengths_skip[word_len] = 1
            else:
                word_lengths_ffd[word_len].append(word.word_first_fixation_duration)
                word_lengths_tft[word_len].append(word.word_total_fix_time)
                word_lengths_skip[word_len] += 1
        else:
            skipped += 1

    skip_rate = skipped/len(et_data)
    print("Skip rate:", skip_rate)

    #print(word_lengths)

ordered_wl_ffd = collections.OrderedDict(sorted(word_lengths_ffd.items()))
ordered_wl_tft = collections.OrderedDict(sorted(word_lengths_tft.items()))
ordered_wl_skip = collections.OrderedDict(sorted(word_lengths_skip.items()))

for k,v in ordered_wl_skip.items():
    print(k,np.mean(v))
    plt.scatter(k,np.mean(v))
plt.show()
