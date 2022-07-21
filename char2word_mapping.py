import os
import pandas as pd
from ast import literal_eval
import numpy as np
from collections import Counter

# read interest area reports and convert character-level fixation into word-level gaze features
def get_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

def split_sentences(data):
    sentence_ids = []
    SENT_ID = 1
    sent_end_symbols = ("?", ".", "!", "?'", "!'", )

    for idx, row in data.iterrows():
        sentence_ids.append(SENT_ID)
        # nothing to do for the last word
        if idx != len(data)-1:
            if row.paragraphId != data.iloc[idx+1]['paragraphId']:
                SENT_ID += 1
            elif row.word.endswith(sent_end_symbols) and data.iloc[idx+1]['word'][0].isupper():
                SENT_ID += 1

    sent_lengths = Counter(sentence_ids)
    print("mean sent. length:", np.mean(list(sent_lengths.values())))
    print("number of sents:", len(list(set(sentence_ids))))
    return sentence_ids

report_dir = "InterestAreaReports/"

trial_areas_df = pd.DataFrame(columns=['part', 'trialId','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])

for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t")#, converters={"INTEREST_AREA_FIXATION_SEQUENCE": literal_eval})
        trials = data.groupby(["TRIAL_INDEX"])
        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        print(subject)
        for trial_no, trial_data in trials:
            char_map = {}
            word2char = {}
            for cidx, c in enumerate(trial_data["IA_LABEL"].values):
                char_map[cidx+1] = c

            part = get_part(trial_data['speechid'].unique()[0])
            #word_ias = pd.read_csv('aois/new_aois/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias', delimiter="\t", header=None)
            word_ias = pd.read_csv('aois/new_aois_fixed_first_last/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias', delimiter="\t", header=None, index_col=False, names=["type", "number", "left", "top", "right", "bottom", "label"])
            # remove interest areas from trials with comprehension questions
            word_ias = word_ias[~word_ias['type'].str.startswith("-")]

            trial_char_ind = 1

            for widx, word in enumerate(word_ias["label"].values):
                word2char[widx+1] = []
                for c in word:
                    if char_map[trial_char_ind] == c:
                        word2char[widx+1].append(trial_char_ind)
                    trial_char_ind += 1

                characters = [char_map[id] for id in word2char[widx+1]]
                word_data = [[part, trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0], widx+1, word, str(characters), str(word2char[widx+1])]]
                word_data_df = pd.DataFrame(word_data, columns=['part', 'trialId','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])
                trial_areas_df = pd.concat([trial_areas_df, word_data_df])
trial_areas_df.drop_duplicates(inplace=True)

trial_areas_df.reset_index(inplace=True)
# split sentences to add sentence ids
sentence_ids = split_sentences(trial_areas_df)
trial_areas_df['sentenceId'] = sentence_ids
print(len(trial_areas_df), "interest areas.")
trial_areas_df.to_csv("word2char_IA_mapping.csv", index=False, encoding='utf-8')
