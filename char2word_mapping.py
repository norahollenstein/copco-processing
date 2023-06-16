from helpers import get_experiment_part, split_sentences
import os
import pandas as pd
from ast import literal_eval
import numpy as np

# read interest area reports and convert character-level fixation into word-level gaze features
# this script also includes the sentence splitting


report_dir = "InterestAreaReports/"

trial_areas_df = pd.DataFrame(columns=['part','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])

for file in os.listdir(report_dir):
    if file.startswith("IA_report_"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", quotechar='"', doublequote=False)#, converters={"INTEREST_AREA_FIXATION_SEQUENCE": literal_eval})

        speeches = data.groupby(["speechid"])
        for speech_no, speech_data in speeches:
            #print(speech_no, trial_areas_df['speechId'].unique())
            if speech_no not in trial_areas_df['speechId'].unique():

                trials = speech_data.groupby(["TRIAL_INDEX"])
                subject = speech_data['RECORDING_SESSION_LABEL'].unique()[0]
                for trial_no, trial_data in trials:
                    char_map = {}
                    word2char = {}
                    for cidx, c in enumerate(trial_data["IA_LABEL"].values):
                        char_map[cidx+1] = c

                    part = get_experiment_part(trial_data['speechid'].unique()[0])
                    speechId = int(trial_data.speechid.values[0])
                    paragraphId = int(trial_data.paragraphid.values[0])

                    #print(part, trial_no, paragraphId, speechId)
                    word_ias = pd.read_csv('aois/aois_fixed_aug22/part'+part+'_IA_'+str(speechId).strip()+'_'+str(paragraphId).strip()+'_words.ias', delimiter="\t", header=None, index_col=False, quoting=3, names=["type", "number", "left", "top", "right", "bottom", "label"])

                    # remove interest areas from trials with comprehension questions
                    word_ias = word_ias[~word_ias['type'].str.startswith("-")]

                    trial_char_ind = 1

                    for widx, word in enumerate(word_ias["label"].values):
                        word2char[widx] = []
                        #print(word)
                        for c in word:
                            if char_map[trial_char_ind] == c:
                                word2char[widx].append(trial_char_ind)
                            trial_char_ind += 1

                        characters = [char_map[id] for id in word2char[widx]]
                        word_data = [[part, trial_data.speechid.values[0], trial_data.paragraphid.values[0], widx, word, str(characters), str(word2char[widx])]]
                        word_data_df = pd.DataFrame(word_data, columns=['part','speechId', 'paragraphId', 'wordId', 'word', 'characters', 'char_IA_ids'])
                        trial_areas_df = pd.concat([trial_areas_df, word_data_df])
            else:
                #print(speech_no, " already done!")
                continue

trial_areas_df.drop_duplicates(inplace=True)
trial_areas_df.reset_index(inplace=True)

# split sentences to add sentence ids
sentence_ids = split_sentences(trial_areas_df)
trial_areas_df['sentenceId'] = sentence_ids
print(len(trial_areas_df), "interest areas.")
trial_areas_df.to_csv("word2char_IA_mapping.csv", index=False, encoding='utf-8')
