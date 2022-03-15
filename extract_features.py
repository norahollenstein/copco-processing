import os
import pandas as pd
import numpy as np
from ast import literal_eval
import sys

def get_experiment_part(speechid):
    #print(speechid)
    experiment_parts = {"1": [1327, 7905, 18561, 18473, 11171, 12063, 26670, 18670, 7946, 22811, 26682], "2": [1317, 1125, 7856, 10365, 1323, 7797, 1165, 1318, 10440, 17526]}
    for k,v in experiment_parts.items():
        if speechid in v:
            part = k
    return part

# This script reads fixation reports from SR Data Vierwer and convert fixation events into character-level and word-level gaze features

word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})

report_dir = "FixationReports/"
output_dir = "ExtractedFeatures/"

for file in os.listdir(report_dir):
    if file.endswith("-utf8.txt"):
        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", converters={"CURRENT_FIX_INTEREST_AREAS": literal_eval})
        print("Texts:", data['speechid'].unique())

        # remove practice speech with ID 1327 and trials with ID -1 (new text screen)
        data = data.drop(data[data.speechid == 1327].index)
        data = data.drop(data[data.paragraphid == -1].index)

        # check which experiment part was conducted
        experiment_parts = []
        for speech_id in data['speechid'].unique():
            experiment_parts.append(get_experiment_part(speech_id))
        if len(list(set(experiment_parts))) > 1:
            print("ERROR! More than one experiment part in fixaton report.")
            sys.exit()

        subject = data['RECORDING_SESSION_LABEL'].unique()[0]
        words_df = pd.DataFrame()

        # split data into trials (1 trial = 1 screen)
        trials = data.groupby(["TRIAL_INDEX"])

        for trial_no, trial_data in trials:

            #print("...")

            # ---- TO DO ----
            # map fixations that fall outside of interest areas but are close enough
            # especially the for the first and last line on the screen. the interest areas of these lines seems to be of shorter height than the rest.
            # use CURRENT_FIX_NEAREST_INTEREST_AREA_LABEL with a threshold on CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE

            trial_word_data = word2char_mapping[(word2char_mapping["trialId"] == trial_no) & (word2char_mapping["paragraphId"] == trial_data.paragraphid.unique()[0]) & (word2char_mapping["part"] == int(experiment_parts[0]))].copy()
            # drop ID -1 here too (new text screen)
            trial_word_data = trial_word_data.drop(trial_word_data[trial_word_data.paragraphId == -1].index)
            trial_word_data = trial_word_data.reset_index()
            trial_word_data.loc[:, 'word_total_fix_dur'] = 0
            trial_word_data.loc[:, 'word_mean_fix_dur'] = 0
            trial_word_data.loc[:, 'word_first_pass_dur'] = 0
            trial_word_data.loc[:, 'word_go_past_time'] = 0
            trial_word_data.loc[:, "word_first_fix_dur"] = 0
            trial_word_data.loc[:, 'landing_position'] = None
            trial_word_data.loc[:, 'number_of_fixations'] = 0
            trial_word_data['fixation_durs'] = [list() for x in range(len(trial_word_data.index))]
            #trial_word_data['fixed_chars'] = [list() for x in range(len(trial_word_data.index))]
            trial_word_data['trial_fix_ids'] = [list() for x in range(len(trial_word_data.index))]

            for fix_id, fix_info in trial_data.iterrows():
                if fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'] != ".":

                    for widx, char_id_list in enumerate(trial_word_data['char_IA_ids']):

                        if int(fix_info['CURRENT_FIX_INTEREST_AREA_ID']) in char_id_list:
                            trial_word_data.at[widx, 'word_total_fix_dur'] += fix_info['CURRENT_FIX_DURATION']
                            trial_word_data.at[widx, 'number_of_fixations'] += 1
                            trial_word_data.at[widx, 'fixation_durs'].append(fix_info['CURRENT_FIX_DURATION'])
                            #trial_word_data.at[widx, 'fixed_chars'].append(fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'])
                            trial_word_data.at[widx, 'trial_fix_ids'].append(fix_id)
                            if trial_word_data.at[widx, 'word_first_fix_dur'] == 0:
                                trial_word_data.at[widx, 'word_first_fix_dur'] = fix_info['CURRENT_FIX_DURATION']
                            if trial_word_data.at[widx, 'landing_position'] == None:
                                trial_word_data.at[widx, 'landing_position'] = fix_info['CURRENT_FIX_INTEREST_AREA_ID']

            # now process word features that need previously added char fixations
            fixations_to_left_of_curr_fix = []
            for word_ind, word in trial_word_data.iterrows():

                if len(word["fixation_durs"]) != 0:
                    trial_word_data.loc[word_ind, 'word_mean_fix_dur'] = np.mean(word['fixation_durs'])
                    go_past_fix = []
                    first_pass_fix = []

                    for idx, f in enumerate(word['trial_fix_ids']):
                        if idx == 0:
                            go_past_fix.append(f)
                            first_pass_fix.append(f)
                            if idx != len(word['trial_fix_ids'])-1:
                                i = 1
                                while f+i in fixations_to_left_of_curr_fix:
                                    go_past_fix.append(f+i)
                                    i +=1
                        else:
                            if f == go_past_fix[-1]+1:
                                go_past_fix.append(f)
                            if f == first_pass_fix[-1]+1:
                                first_pass_fix.append(f)
                        fixations_to_left_of_curr_fix.append(f)

                    for fix_ind in first_pass_fix:
                        trial_word_data.loc[word_ind, 'word_first_pass_dur'] += trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']
                    for fix_ind in go_past_fix:
                        trial_word_data.loc[word_ind, 'word_go_past_time'] += trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']

            words_df = pd.concat([words_df, trial_word_data], ignore_index=True)
        words_df.to_csv(output_dir+subject+".csv")
