import pandas as pd
import numpy as np
import math
import collections
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
from scipy.ndimage.filters import gaussian_filter1d
import string
import scipy

#test word length effect
#test word frequency effect
#test omission rate/skipping

def first_char_analysis(et_data, subject):
    """Analyze dwell time on the first character between vowels and consonants"""

    dwell_time_vowels = {}
    dwell_time_punct = {}
    dwell_time_consonants = {}

    vowels = "aeiouæøåyé"
    punct = ".,?!:;-()'1234567890"
    print(subject)

    for index, word in et_data.iterrows():
        word_len = len(word.word)
        if not math.isnan(word.word_first_char_dwell_time):
            #print(word.word, word.word_landing_position_char, word.word_landing_position_index, word.word_first_char_dwell_time)
            if word.word_landing_position_char.lower() in vowels:
                if word.word_landing_position_char.lower() not in dwell_time_vowels:
                    dwell_time_vowels[word.word_landing_position_char.lower()] = [word.word_first_char_dwell_time]
                else:
                    dwell_time_vowels[word.word_landing_position_char.lower()].append(word.word_first_char_dwell_time)
            elif word.word_landing_position_char.lower() in punct:
                if word.word_landing_position_char.lower() not in dwell_time_punct:
                    dwell_time_punct[word.word_landing_position_char.lower()] = [word.word_first_char_dwell_time]
                else:
                    dwell_time_punct[word.word_landing_position_char.lower()].append(word.word_first_char_dwell_time)
            else:
                if word.word_landing_position_char.lower() not in dwell_time_consonants:
                    dwell_time_consonants[word.word_landing_position_char.lower()] = [word.word_first_char_dwell_time]
                else:
                    dwell_time_consonants[word.word_landing_position_char.lower()].append(word.word_first_char_dwell_time)

    flat_vowel_list = [item for sublist in dwell_time_vowels.values() for item in sublist]
    flat_cons_list = [item for sublist in dwell_time_consonants.values() for item in sublist]
    print("vowels mean:", np.mean(flat_vowel_list))
    print("consonants mean:", np.mean(flat_cons_list))
    print(scipy.stats.ttest_ind(flat_vowel_list, flat_cons_list))

def word_length_effect(et_data, subject):
    """Analyze word length effect"""

    word_lengths_ffd = {}
    word_lengths_tft = {}
    word_lengths_skip = {}

    skipped = 0
    for index, word in et_data.iterrows():
        word_len = len(word.word)
        if not math.isnan(word.word_first_fixation_duration):
            if word_len not in word_lengths_skip:
                #word_lengths_ffd[word_len] = [word.word_first_fixation_duration]
                #word_lengths_tft[word_len] = [word.word_total_fix_time]
                # skiped: (skiped words of this length, total no. of words of this length)
                word_lengths_skip[word_len] = [1,1]
            else:
                #word_lengths_ffd[word_len].append(word.word_first_fixation_duration)
                #word_lengths_tft[word_len].append(word.word_total_fix_time)
                word_lengths_skip[word_len][0] += 1
                word_lengths_skip[word_len][1] += 1
        else:
            skipped += 1
            if word_len not in word_lengths_skip:
                word_lengths_skip[word_len] = [0,1]
            else:
                word_lengths_skip[word_len][1] += 1

    skip_rate = 1-skipped/len(et_data)
    print("Skipping rate:", subject, skip_rate)

    return word_lengths_skip

def plot_word_len_effect(skipping_proportions):
    #ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", units="subj", estimator=None, lw=1, alpha=0.3)
    ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", ci="sd", label="mean")

    plt.ylim(0,1)
    plt.xlim(1,25)
    plt.legend([],[], frameon=False)
    #plt.title("Word length effect")
    plt.xlabel("word length")
    plt.savefig("plots/word_length_effect_copco.pdf")
    plt.show()

def plot_feat_ranges(et_data_all_subjs):

    features = ["word_first_fixation_duration", "word_first_char_dwell_time", "word_total_fix_time"] #"word_gaze_duration","word_go_past_time"
    print(list(et_data_all_subjs['word_first_char_dwell_time']))

    sns.set(font_scale = 1)
    sns.set_style("whitegrid")

    ax = sns.boxplot(data=et_data_all_subjs[features], palette=sns.color_palette("hls", len(features)), color='grey', linewidth=1, fliersize=1)
    medians = []
    for f in features:
        print(f, "mean/std:", np.mean(et_data_all_subjs[f]), np.std(et_data_all_subjs[f]))
        median = et_data_all_subjs[f].median()
        medians.append(median)
    median_labels = [str(np.round(s, 2)) for s in medians]

    pos = range(len(medians))
    for tick,label in zip(pos,ax.get_xticklabels()):
        ax.text(pos[tick], -200, median_labels[tick], #medians[tick] + offsets[tick]
                horizontalalignment='center', size='small', color='black')#, weight='semibold')

    plt.savefig("plots/feature_ranges_copco.pdf")
    plt.show()
    plt.close()

    #ax = sns.boxplot(data=et_data_all_subjs[["number_of_fixations"]], color="green")
    #plt.show()

def main():

    indir = 'word_feature_reports/'

    skipping_proportions = pd.DataFrame(columns=["subj", "word_len", "skip"])
    et_data_all_subjs = pd.DataFrame()

    for file in os.listdir(indir):
        if file.endswith(".csv"):
            subject = file[:3]
            et_data = pd.read_csv(os.path.join(indir, file))
            # remove practice trials
            et_data = et_data.drop(et_data[et_data.speechId == 1327].index)
            # remove beginning of speech trials
            et_data = et_data.drop(et_data[et_data.paragraphId == -1].index)
            et_data_all_subjs = pd.concat([et_data_all_subjs, et_data])

            wl_skip = word_length_effect(et_data, subject)
            #first_char_analysis(et_data, subject)

            for k,v in wl_skip.items():
                skipping_proportions = skipping_proportions.append({"subj":subject, "word_len":k, "skip": 1-v[0]/v[1]}, ignore_index=True)

    plot_word_len_effect(skipping_proportions)
    #plot_feat_ranges(et_data_all_subjs)
    #first_char_analysis(et_data_all_subjs, "ALL")








if __name__ == "__main__":
    main()
