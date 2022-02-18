import os
import pandas as pd
import numpy as np
from ast import literal_eval

# read fixation reports from SR Data Vierwer and convert fixation events into character-level and word-level gaze features

word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})

report_dir = "FixationReports/"
for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", converters={"CURRENT_FIX_INTEREST_AREAS": literal_eval})#, "CURRENT_FIX_INTEREST_AREA_DATA": literal_eval, "NEXT_FIX_INTEREST_AREAS": literal_eval, "NEXT_FIX_INTEREST_AREA_DATA": literal_eval, "NEXT_SAC_END_INTEREST_AREAS": literal_eval})
        print(data['speechid'].unique())

        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        print(subject)
        word_df = pd.DataFrame(columns=['trialId','speechId', 'paragraphId', 'wordId', 'word', 'word_fixated', 'number_of_fixations', 'word_landing_position_char', 'word_landing_position_index', 'word_first_fixation_duration', 'word_mean_fixation_duration', 'word_first_char_dwell_time', 'word_total_fix_time', 'word_gaze_duration', 'word_go_past_time'])

        # split data into trials (1 trial = 1 screen)
        trials = data.groupby(["TRIAL_INDEX"])
        for trial_no, trial_data in trials:
            # maps fixation indices to interest area labels
            char_map = {}
            char_map = dict(zip(trial_data["CURRENT_FIX_INDEX"], trial_data["CURRENT_FIX_INTEREST_AREA_ID"]))
            #print(char_map)

            # ---- TO DO ----
            # map fixations that fall outside of interest areas but are close enough
            # use CURRENT_FIX_NEAREST_INTEREST_AREA_LABEL with a threshold on CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE

            for char_id in trial_data["CURRENT_FIX_INTEREST_AREA_ID"].tolist():
                word = word2char_mapping.loc[char_id in word2char_mapping['char_IA_ids'], 'word']
                trial_data.loc[trial_data["CURRENT_FIX_INTEREST_AREA_ID"]==char_id, 'word'] = word

            #trial_data["word"] = word2char_mapping.loc[trial_data["CURRENT_FIX_INTEREST_AREA_ID"] in word2char_mapping['char_IA_ids'], 'word']
            print(trial_data)

            # then: group trial data by word
