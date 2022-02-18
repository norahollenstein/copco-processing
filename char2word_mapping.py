import os
import pandas as pd
from ast import literal_eval
import numpy as np

# read interest area reports and convert character-level fixation into word-level gaze features
def get_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

report_dir = "InterestAreaReports/"

trial_areas_df = pd.DataFrame(columns=['part', 'trialId','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])

for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t")#, converters={"INTEREST_AREA_FIXATION_SEQUENCE": literal_eval})
        #print(data['speechid'].unique())
        trials = data.groupby(["TRIAL_INDEX"])
        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        print(subject)
        for trial_no, trial_data in trials:
            char_map = {}
            word2char = {}
            for cidx, c in enumerate(trial_data["IA_LABEL"].values):
                char_map[cidx+1] = c

            part = get_part(trial_data['speechid'].unique()[0])
            word_ias = pd.read_csv('aois/new_aois/part'+part+'_IA_'+str(trial_data.speechid.values[0]).strip()+'_'+str(trial_data.paragraphid.values[0]).strip()+'_words.ias', delimiter="\t", header=None)
            trial_char_ind = 1
            for widx, word in enumerate(word_ias[6].values):
                word2char[widx+1] = []
                for c in word:
                    if char_map[trial_char_ind] == c:
                        word2char[widx+1].append(trial_char_ind)
                    trial_char_ind += 1
                characters = [char_map[id] for id in word2char[widx+1]]
                word_data = [[part, trial_no, trial_data.speechid.values[0], trial_data.paragraphid.values[0], widx+1, word, str(characters), str(word2char[widx+1])]]
                #print(word_data)
                word_data_df = pd.DataFrame(word_data, columns=['part', 'trialId','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])
                trial_areas_df = pd.concat([trial_areas_df, word_data_df])
                #trial_areas_df.drop_duplicates(inplace=True)
        print(len(trial_areas_df))
print(len(trial_areas_df))
trial_areas_df.drop_duplicates(inplace=True)
print(len(trial_areas_df))
trial_areas_df.to_csv("word2char_IA_mapping.csv", index=False, encoding='utf-8')
