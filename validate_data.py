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
from wordfreq import word_frequency, zipf_frequency
from scipy import stats

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


def word_freq_effect(et_data, subject):
    """Analyze word length effect"""

    word_freqs_ffd = {}
    word_freqs_tft = {}
    word_freqs_skip = {}

    #dk_frequency_list = pd.read_csv("lemma-10k-2017/lemma-10k-2017-in.txt", delimiter="\t", header=None, names=['pos', 'word', 'freq'])

    skipped = 0
    for index, word in et_data.iterrows():
        # base-10 logarithm of the number of times it appears per billion words
        word_freq = word_frequency(word.word, 'da')
        word_freq = round(word_freq, 3)
        #word_freq = dk_frequency_list[dk_frequency_list['word'] == word.word].freq
        if not math.isnan(word.word_first_fixation_duration):
            if word_freq not in word_freqs_skip:
                #word_lengths_ffd[word_len] = [word.word_first_fixation_duration]
                #word_lengths_tft[word_len] = [word.word_total_fix_time]
                # skiped: (skiped words of this length, total no. of words of this length)
                word_freqs_skip[word_freq] = [1,1]
            else:
                #word_lengths_ffd[word_len].append(word.word_first_fixation_duration)
                #word_lengths_tft[word_len].append(word.word_total_fix_time)
                word_freqs_skip[word_freq][0] += 1
                word_freqs_skip[word_freq][1] += 1
        else:
            skipped += 1
            if word_freq not in word_freqs_skip:
                word_freqs_skip[word_freq] = [0,1]
            else:
                word_freqs_skip[word_freq][1] += 1

    skip_rate = 1-skipped/len(et_data)
    print("Skipping rate:", subject, skip_rate)

    return word_freqs_skip

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

    return word_lengths_skip

def plot_word_len_effect(skipping_proportions):
    #ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", units="subj", estimator=None, lw=1, alpha=0.3)
    ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", ci="sd", label="mean")

    plt.ylim(0,1)
    plt.xlim(1,25)
    plt.legend([],[], frameon=False)
    #plt.title("Word length effect")
    plt.xlabel("word length")
    plt.ylabel("skipping proportion")
    plt.savefig("plots/word_length_effect_copco.pdf")
    plt.show()

def plot_word_freq_effect(skipping_proportions):
    #ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", units="subj", estimator=None, lw=1, alpha=0.3)
    ax = sns.lineplot(data=skipping_proportions, x="word_freq", y="skip", ci="sd", label="mean")

    plt.ylim(0.2,1)
    plt.xlim(0,0.031)
    plt.gca().invert_xaxis()
    #ax.set_xticklabels([7,6,5,4,3])
    plt.legend([],[], frameon=False)
    #plt.title("Word length effect")
    plt.xlabel("word frequency")
    plt.ylabel("skipping proportion")
    plt.savefig("plots/word_freq_effect_copco.pdf")
    plt.show()

def plot_feat_ranges(et_data_all_subjs):

    features = ["word_first_fixation_duration", "word_mean_fixation_duration", "word_total_fix_time"]

    sns.set(font_scale = 1)
    sns.set_style("whitegrid")

    print(len(et_data_all_subjs))
    et_data_all_subjs.drop(et_data_all_subjs[et_data_all_subjs.word_mean_fixation_duration < 100].index, inplace=True)
    print(len(et_data_all_subjs))

    ax = sns.boxplot(data=et_data_all_subjs[features], palette=sns.color_palette("Blues_d", len(features)), color='grey', linewidth=1, fliersize=1)
    medians = []
    for f in features:
        print(f, "mean/std:", np.mean(et_data_all_subjs[f]), np.std(et_data_all_subjs[f]))
        median = et_data_all_subjs[f].median()
        mean = np.mean(et_data_all_subjs[f])

        medians.append(mean)
    median_labels = [str(np.round(s, 2)) for s in medians]
    #median_labels = [str(np.round(s, 2)) for s in medians]

    pos = range(len(medians))
    for tick,label in zip(pos,ax.get_xticklabels()):
        ax.text(pos[tick], -220, median_labels[tick], #medians[tick] + offsets[tick]
                horizontalalignment='center', size='small', color='black')#, weight='semibold')
    ax.set_xticklabels(["FFD", "MFD", "TFT"])
    plt.ylim(0,2000)
    plt.savefig("plots/feature_ranges_copco.pdf")
    plt.show()
    plt.close()

    #ax = sns.boxplot(data=et_data_all_subjs[["number_of_fixations"]], color="green")
    #plt.show()



def plot_landing_position(et_data_all_subjs):

    all_df = pd.DataFrame(columns = ['position', 'count'])
    for n in et_data_all_subjs['word_landing_position_index'].unique():
        x = len(et_data_all_subjs[et_data_all_subjs['word_landing_position_index'] == n])

        if x != 0 and n <13:
            dd = [[int(n+1), x]]
            df = pd.DataFrame(dd, columns = ['position', 'count'])
            all_df = pd.concat([all_df, df])


    sns.set(font_scale = 1)
    sns.set_style("whitegrid")
    ax = sns.barplot(x="position", y="count", data=all_df, palette="Blues_d")

    plt.savefig("plots/landing_pos_copco.pdf")
    plt.show()
    plt.close()

def landing_pos_freq(et_data_all_subjs):
    char_freq = pd.read_csv("letter_freq_dk.csv", header=0)
    chars = et_data_all_subjs.word_landing_position_char.tolist()
    chars = [str(x) for x in chars if str(x) != 'nan']

    freq_dict = {}
    freq_dict_char = {}

    for idx,row in et_data_all_subjs.iterrows():
        #print(row.word_landing_position_char)
        if str(row.word_landing_position_char) != "nan":
            #print(row.word_landing_position_char)
            #print(char_freq[char_freq.Letter == str(row.word_landing_position_char).upper()].Frequency.values[0])
            try:
                freq = char_freq[char_freq.Letter == str(row.word_landing_position_char).upper()].Frequency.values[0]
                if float(freq) not in freq_dict:
                    freq_dict[float(freq)] = 1
                else:
                    freq_dict[float(freq)] += 1
                if str(row.word_landing_position_char).upper() not in freq_dict_char:
                    freq_dict_char[str(row.word_landing_position_char).upper()] = 1
                else:
                    freq_dict_char[str(row.word_landing_position_char).upper()] += 1
            except IndexError:
                continue

    normalized = []
    for x,y in freq_dict.items():
        normalized.append(y/x)

    print("landing pos frequency")
    print(stats.spearmanr(list(freq_dict.keys()), normalized))

def landing_pos_word_len(et_data_all_subjs):
    char_freq = pd.read_csv("letter_freq_dk.csv", header=0)
    chars = et_data_all_subjs.word_landing_position_char.tolist()
    chars = [str(x) for x in chars if str(x) != 'nan']

    wl_dict = {}
    #wl_dict_chars = {}

    for idx,row in et_data_all_subjs.iterrows():
        #print(row.word_landing_position_char)
        if row.word_landing_position_index >= 0:
            wl = len(row.word)
            #print(row.word, wl, row.word_landing_position_index)
            if wl not in wl_dict:
                wl_dict[wl] = [row.word_landing_position_index]
            else:
                wl_dict[wl].append(row.word_landing_position_index)

    means = []
    for x,y in wl_dict.items():
        means.append(np.mean(y))
    #print(freq_dict_char)
    df = pd.DataFrame({"wl": list(wl_dict.keys()), "pos": means})

    sns.set(font_scale = 1)
    sns.set_style("whitegrid")
    ax = sns.barplot(x="wl", y="pos", data=df, palette="Blues_d")

    plt.savefig("plots/landing_pos_wl_copco.pdf")
    plt.show()
    plt.close()

    print("landing pos word len")
    print(stats.spearmanr(list(wl_dict.keys()), means))



def main():

    indir = 'word_feature_reports/'

    skipping_proportions = pd.DataFrame(columns=["subj", "word_len", "skip"])
    skipping_proportions_freq = pd.DataFrame(columns=["subj", "word_freq", "skip"])
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
            wf_skip = word_freq_effect(et_data, subject)
            #first_char_analysis(et_data, subject)

            for k,v in wl_skip.items():
                skipping_proportions = skipping_proportions.append({"subj":subject, "word_len":k, "skip": 1-v[0]/v[1]}, ignore_index=True)
            for k,v in wf_skip.items():
                skipping_proportions_freq = skipping_proportions_freq.append({"subj":subject, "word_freq":k, "skip": 1-v[0]/v[1]}, ignore_index=True)


    #plot_word_len_effect(skipping_proportions)
    #plot_word_freq_effect(skipping_proportions_freq)
    #plot_feat_ranges(et_data_all_subjs)
    #print(et_data_all_subjs['word_landing_position_index'].unique())
    #plot_landing_position(et_data_all_subjs)
    #first_char_analysis(et_data_all_subjs, "ALL")
    #landing_pos_freq(et_data_all_subjs)
    #landing_pos_word_len(et_data_all_subjs)
    print(np.nanmean(et_data_all_subjs['number_of_fixations'].tolist()), np.nanstd(et_data_all_subjs['number_of_fixations'].tolist()))








if __name__ == "__main__":
    main()
