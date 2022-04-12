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
from ast import literal_eval


#test word length effect
#test word frequency effect
#test omission rate/skipping

def first_char_analysis(et_data, subject):
    """Analyze dwell time on the first character between vowels and consonants"""

    dwell_time_vowels = {}
    dwell_time_punct = {}
    dwell_time_consonants = {}

    vowels = "aeiouæøåy"
    punct = ".,?!:;-()'1234567890[]%/’”äé⁄–, "
    print(subject)

    for index, word in et_data.iterrows():
        word_len = len(word.word)
        if not math.isnan(word.word_first_fix_dur):
            # get actual character from index
            landing_position_char = word.word[int(word.landing_position)]
            landing_position_char = landing_position_char.lower()

            if landing_position_char in vowels:
                if landing_position_char not in dwell_time_vowels:
                    dwell_time_vowels[landing_position_char] = [word.word_first_fix_dur]
                else:
                    dwell_time_vowels[landing_position_char].append(word.word_first_fix_dur)
            elif landing_position_char in punct:
                if landing_position_char not in dwell_time_punct:
                    dwell_time_punct[landing_position_char] = [word.word_first_fix_dur]
                else:
                    dwell_time_punct[landing_position_char].append(word.word_first_fix_dur)
            else:
                if landing_position_char not in dwell_time_consonants:
                    dwell_time_consonants[landing_position_char] = [word.word_first_fix_dur]
                else:
                    dwell_time_consonants[landing_position_char].append(word.word_first_fix_dur)

    flat_vowel_list = [item for sublist in dwell_time_vowels.values() for item in sublist]
    flat_cons_list = [item for sublist in dwell_time_consonants.values() for item in sublist]
    print("vowels mean:", np.mean(flat_vowel_list), len(flat_vowel_list))
    print("consonants mean:", np.mean(flat_cons_list), len(flat_cons_list))
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
        if not math.isnan(word.word_first_fix_dur):
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
        if not math.isnan(word.word_first_fix_dur):
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
    ax = sns.lineplot(data=skipping_proportions, x="word_len", y="skip", ci="sd", label="mean")

    plt.ylim(0,1)
    plt.xlim(1,25)
    plt.legend([],[], frameon=False)
    plt.xlabel("word length")
    plt.ylabel("skipping proportion")
    plt.savefig("plots/word_length_effect_copco.pdf")
    plt.show()

def plot_word_freq_effect(skipping_proportions):
    ax = sns.lineplot(data=skipping_proportions, x="word_freq", y="skip", ci="sd", label="mean")

    plt.ylim(0.2,1)
    plt.xlim(0,0.031)
    plt.legend([],[], frameon=False)
    plt.xlabel("word frequency")
    plt.ylabel("skipping proportion")
    plt.savefig("plots/word_freq_effect_copco.pdf")
    plt.show()

def plot_feat_ranges(et_data_all_subjs):

    features = ["word_first_fix_dur", "word_mean_fix_dur", "word_total_fix_dur", "word_first_pass_dur", "word_go_past_time"]#, "word_mean_sacc_dur", "word_peak_sacc_velocity"]
    #features = ["number_of_fixations"] # "number_of_fixations"

    sns.set(font_scale = 1)
    sns.set_style("whitegrid")

    print(len(et_data_all_subjs))
    et_data_all_subjs.drop(et_data_all_subjs[et_data_all_subjs.word_mean_fix_dur < 100].index, inplace=True)
    print(len(et_data_all_subjs))

    ax = sns.boxplot(data=et_data_all_subjs[features], palette=sns.color_palette("viridis", len(features)), color='grey', linewidth=1, fliersize=1)
    medians = []
    for f in features:
        print(f, "mean/std:", np.nanmean(et_data_all_subjs[f]), np.nanmedian(et_data_all_subjs[f]), np.std(et_data_all_subjs[f]))
        median = np.nanmedian(et_data_all_subjs[f])
        medians.append(median)
    median_labels = [str(np.round(s, 2)) for s in medians]

    pos = range(len(median_labels))
    for tick,label in zip(pos,ax.get_xticklabels()):
        ax.text(pos[tick], -220, median_labels[tick], #medians[tick] + offsets[tick]
                horizontalalignment='center', size='small', color='black')#, weight='semibold')
    ax.set_xticklabels(["FFD", "MFD", "TFD", "FPD", "GPT"])
    plt.ylim(0,2000)
    plt.savefig("plots/feature_ranges_copco.pdf")
    plt.show()
    plt.close()


def plot_landing_position(et_data_all_subjs):

    all_df = pd.DataFrame(columns = ['position', 'count'])
    for n in et_data_all_subjs['landing_position'].unique():
        x = len(et_data_all_subjs[et_data_all_subjs['landing_position'] == n])

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
    # source: https://www.sttmedia.com/characterfrequency-danish
    char_freq = pd.read_csv("utils/letter_freq_dk.csv", header=0, delimiter=";")

    # get actual characters from index
    chars = []
    for index, word in et_data_all_subjs.iterrows():
        if not math.isnan(word.word_first_fix_dur):
            char = word.word[int(word.landing_position)].lower()
            chars.append(char)
    chars = [str(x) for x in chars if str(x) != 'nan']

    freq_dict = {}
    freq_dict_char = {}

    for char in chars:
        try:
            freq = char_freq[char_freq.Letter == str(char).upper()].Frequency.values[0]
            freq = freq.replace("%", "")
            freq = freq.replace(" ", "")
            if float(freq) not in freq_dict:
                freq_dict[float(freq)] = 1
            else:
                freq_dict[float(freq)] += 1
            if str(char).upper() not in freq_dict_char:
                freq_dict_char[str(char).upper()] = 1
            else:
                freq_dict_char[str(char).upper()] += 1
        except IndexError:
            continue

    normalized = []
    for x,y in freq_dict.items():
        normalized.append(y/x)

    print("landing pos frequency")
    print(stats.spearmanr(list(freq_dict.keys()), normalized))

def landing_pos_word_len(et_data_all_subjs):

    wl_dict = {}

    for idx,row in et_data_all_subjs.iterrows():
        if row.landing_position >= 0:
            wl = len(row.word)
            #print(row.word, wl, row.word_landing_position_index)
            if wl not in wl_dict:
                wl_dict[wl] = [row.landing_position]
            else:
                wl_dict[wl].append(row.landing_position)

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

    indir = 'ExtractedFeatures/'

    skipping_proportions = pd.DataFrame(columns=["subj", "word_len", "skip"])
    skipping_proportions_freq = pd.DataFrame(columns=["subj", "word_freq", "skip"])
    et_data_all_subjs = pd.DataFrame()

    for file in os.listdir(indir):
        if file.endswith(".csv"):
            subject = file[:3]
            if int(subject[-2:]) <= 22: # <=22 for typical readers, >=23 for dyslexic participants
                et_data = pd.read_csv(os.path.join(indir, file), converters={"char_IA_ids": literal_eval})
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

    # Basic data validation
    plot_word_len_effect(skipping_proportions)
    plot_word_freq_effect(skipping_proportions_freq)
    #plot_feat_ranges(et_data_all_subjs)

    # Landing position analyses
    """
    plot_landing_position(et_data_all_subjs)
    first_char_analysis(et_data_all_subjs, "ALL")
    landing_pos_freq(et_data_all_subjs)
    landing_pos_word_len(et_data_all_subjs)
    """

    # Total number of fixations across all participants
    print(et_data_all_subjs['number_of_fixations'].sum)








if __name__ == "__main__":
    main()
