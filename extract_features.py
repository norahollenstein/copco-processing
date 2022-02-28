import os
import pandas as pd
import numpy as np
from ast import literal_eval
import sys

# read fixation reports from SR Data Vierwer and convert fixation events into character-level and word-level gaze features

word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})
#print(word2char_mapping)

#char_mapping_part1 = pd.read_csv("part1_char_areas.csv", header=0)
#char_mapping_part2 = pd.read_csv("part2_char_areas.csv", header=0)
#char_mapping = pd.concat([char_mapping_part1, char_mapping_part2])

report_dir = "FixationReports/"
output_dir = "ExtractedFeatures/"

for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", converters={"CURRENT_FIX_INTEREST_AREAS": literal_eval})#, "CURRENT_FIX_INTEREST_AREA_DATA": literal_eval, "NEXT_FIX_INTEREST_AREAS": literal_eval, "NEXT_FIX_INTEREST_AREA_DATA": literal_eval, "NEXT_SAC_END_INTEREST_AREAS": literal_eval})
        print("Texts:", data['speechid'].unique())

        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        words_df = pd.DataFrame()

        # split data into trials (1 trial = 1 screen)
        trials = data.groupby(["TRIAL_INDEX"])

        for trial_no, trial_data in trials:

            # ignore practice speech with ID 1327 and sentences with ID -1 (new text screen)
            if trial_data['speechid'].tolist()[0] != 1327 or trial_data['paragraphid'].tolist()[0] != -1:

                # ---- TO DO ----
                # map fixations that fall outside of interest areas but are close enough
                # use CURRENT_FIX_NEAREST_INTEREST_AREA_LABEL with a threshold on CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE

                trial_word_data = word2char_mapping[word2char_mapping["trialId"] == trial_no].copy()
                trial_word_data = trial_word_data.reset_index()
                trial_word_data.loc[:, 'word_total_fix_dur'] = 0
                trial_word_data.loc[:, 'word_mean_fix_dur'] = 0
                trial_word_data.loc[:, 'word_first_past_dur'] = 0
                trial_word_data.loc[:, "word_first_fix_dur"] = 0
                trial_word_data.loc[:, 'landing_position'] = None
                trial_word_data.loc[:, 'number_of_fixations'] = 0
                trial_word_data['fixation_durs'] = [list() for x in range(len(trial_word_data.index))]
                trial_word_data['fixed_chars'] = [list() for x in range(len(trial_word_data.index))]
                trial_word_data['trial_fix_ids'] = [list() for x in range(len(trial_word_data.index))]

                for fix_id, fix_info in trial_data.iterrows():
                    if fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'] != ".":

                        for widx, char_id_list in enumerate(trial_word_data['char_IA_ids']):

                            if int(fix_info['CURRENT_FIX_INTEREST_AREA_ID']) in char_id_list:
                                trial_word_data.at[widx, 'word_total_fix_dur'] += fix_info['CURRENT_FIX_DURATION']
                                trial_word_data.at[widx, 'number_of_fixations'] += 1
                                trial_word_data.at[widx, 'fixation_durs'].append(fix_info['CURRENT_FIX_DURATION'])
                                trial_word_data.at[widx, 'fixed_chars'].append(fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'])
                                trial_word_data.at[widx, 'trial_fix_ids'].append(fix_id)
                                if trial_word_data.at[widx, 'word_first_fix_dur'] == 0:
                                    trial_word_data.at[widx, 'word_first_fix_dur'] = fix_info['CURRENT_FIX_DURATION']
                                if trial_word_data.at[widx, 'landing_position'] == None:
                                    trial_word_data.at[widx, 'landing_position'] = fix_info['CURRENT_FIX_INTEREST_AREA_ID']

                # now process word features that need previously added char fixations
                for word_ind, word in trial_word_data.iterrows():
                    if len(word["fixation_durs"]) != 0:
                        trial_word_data.loc[word_ind, 'word_mean_fix_dur'] = np.mean(word['fixation_durs'])

                        for idx, f in enumerate(word['trial_fix_ids']):
                            if idx == 0:
                                trial_word_data.loc[word_ind, 'word_first_past_dur'] = word['fixation_durs'][0]
                            if idx != len(word['trial_fix_ids'])-1:
                                if word['trial_fix_ids'][idx+1] == f+1:
                                    trial_word_data.loc[word_ind, 'word_first_past_dur'] += word['fixation_durs'][idx+1]

                words_df = pd.concat([words_df, trial_word_data], ignore_index=True)
        words_df.to_csv(output_dir+subject+".csv")




        # --- TODO ---
        # remove sentence with ID -1 and practice speech 1327
