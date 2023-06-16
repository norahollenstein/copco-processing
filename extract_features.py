from helpers import get_experiment_part
import os
import pandas as pd
import numpy as np
from ast import literal_eval
import sys

# This script reads fixation reports from SR Data Vierwer and convert fixation events into character-level and word-level gaze features

# test: speechIDs 18473 and 7905



word2char_mapping = pd.read_csv("word2char_IA_mapping.csv", converters={"characters": literal_eval, "char_IA_ids": literal_eval})
report_dir = "FixationReports/"
output_dir = "ExtractedFeatures/"

TOTAL_FIX = 0
ALL_FIX_IN_IA = 0
UNMAPPED = 0
DIST = 0
dists = []
WORDS = 0

for file in os.listdir(report_dir):
    if file.startswith("FIX_report_"):

        print(file)
        data = pd.read_csv(report_dir+file, delimiter="\t", quotechar='"', doublequote=False, converters={"CURRENT_FIX_INTEREST_AREAS": literal_eval})
        print("Texts:", data['speechid'].unique())

        TOTAL_FIX += len(data)

        # remove practice speech with ID 1327 and trials with ID -1 (new text screen)
        data = data.drop(data[data.speechid == 1327].index)
        data = data.drop(data[data.paragraphid == -1].index)

        # check which experiment part was conducted
        # todo: can this be removed? we get experiment part through char mapping
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
        #print(len(trials))
        #print("----")

        for trial_no, trial_data in trials:
            # todo: count trials - check when there are duplicates?

            #print(trial_no, len(trial_data))

            #print(trial_data['TRIAL_INDEX'].unique(), len(trial_data), trial_data['speechid'].unique())
            #print(len(trial_data))

            # remove all fixations < 100ms as they probably don't contain linguistic processing information
            trial_data = trial_data.drop(trial_data[trial_data.CURRENT_FIX_DURATION < 100].index)
            #print(len(trial_data))

            #print(trial_data['TRIAL_INDEX'].unique(), len(trial_data), trial_data['speechid'].unique())
            #print("---")


            # ---- TO DO ----
            # map fixations that fall outside of interest areas but are close enough
            # especially the for the first and last line on the screen. the interest areas of these lines seems to be of shorter height than the rest.
            # use CURRENT_FIX_NEAREST_INTEREST_AREA_LABEL with a threshold on CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE

            # !!! todo: this should map on speechID and paraID, not trialID! trialID is not equal across participants!!
            trial_word_data = word2char_mapping[(word2char_mapping["speechId"] == trial_data.speechid.unique()[0]) & (word2char_mapping["paragraphId"] == trial_data.paragraphid.unique()[0]) & (word2char_mapping["part"] == int(experiment_parts[0]))].copy()

            # assign this participants trial number
            trial_word_data.loc[:, 'trialId'] = trial_no
            #print(trial_word_data['trialId'].unique(), len(trial_word_data), trial_word_data['speechId'].unique())


            # drop ID -1 here too (new text screen)
            trial_word_data = trial_word_data.drop(trial_word_data[trial_word_data.paragraphId == -1].index)
            # drop columns that are not needed
            trial_word_data = trial_word_data.drop('characters', axis=1)
            # rest index column
            trial_word_data.reset_index(drop=True, inplace=True)

            # initialize word-level eye-tracking features
            # set initial feature values to nan, 0 or empty list
            # fixation features:
            trial_word_data.loc[:, 'word_total_fix_dur'] = np.NaN
            trial_word_data.loc[:, 'word_mean_fix_dur'] = np.NaN
            trial_word_data.loc[:, 'word_first_pass_dur'] = np.NaN
            trial_word_data.loc[:, 'word_go_past_time'] = np.NaN
            trial_word_data.loc[:, "word_first_fix_dur"] = np.NaN
            trial_word_data.loc[:, 'landing_position'] = np.NaN
            trial_word_data.loc[:, 'number_of_fixations'] = 0
            trial_word_data['fixation_durs'] = [list() for x in range(len(trial_word_data.index))]
            trial_word_data['fixed_chars'] = [list() for x in range(len(trial_word_data.index))]
            trial_word_data['trial_fix_ids'] = [list() for x in range(len(trial_word_data.index))]
            # saccade features:
            trial_word_data.loc[:, 'word_mean_sacc_dur'] = np.NaN
            trial_word_data.loc[:, 'word_peak_sacc_velocity'] = np.NaN
            trial_word_data['saccade_durs'] = [list() for x in range(len(trial_word_data.index))]
            trial_word_data['saccade_vels'] = [list() for x in range(len(trial_word_data.index))]

            # iterate through all fixations in a trial
            for fix_id, fix_info in trial_data.iterrows():
                # check that current fixation falls on text
                if fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'] != ".":
                    ALL_FIX_IN_IA += 1
                    for widx, char_id_list in enumerate(trial_word_data['char_IA_ids']):
                        # this only takes the first IA, therefore all IAs falling on a question are automatically out
                        if int(fix_info['CURRENT_FIX_INTEREST_AREA_ID']) in char_id_list:
                            if np.isnan(trial_word_data.at[widx, 'word_total_fix_dur']):
                                trial_word_data.at[widx, 'word_total_fix_dur'] = fix_info['CURRENT_FIX_DURATION']
                            else:
                                trial_word_data.at[widx, 'word_total_fix_dur'] += fix_info['CURRENT_FIX_DURATION']
                            trial_word_data.at[widx, 'number_of_fixations'] += 1
                            trial_word_data.at[widx, 'fixation_durs'].append(fix_info['CURRENT_FIX_DURATION'])
                            trial_word_data.at[widx, 'fixed_chars'].append(fix_info['CURRENT_FIX_INTEREST_AREA_LABEL'])
                            trial_word_data.at[widx, 'trial_fix_ids'].append(fix_id)
                            if np.isnan(trial_word_data.at[widx, 'word_first_fix_dur']):
                                trial_word_data.at[widx, 'word_first_fix_dur'] = fix_info['CURRENT_FIX_DURATION']
                            if np.isnan(trial_word_data.at[widx, 'landing_position']):
                                trial_word_data.at[widx, 'landing_position'] = char_id_list.index(int(fix_info['CURRENT_FIX_INTEREST_AREA_ID']))
                            # check for saccades
                            if fix_info['NEXT_SAC_DURATION'] != ".":
                                trial_word_data.at[widx, 'saccade_durs'].append(int(fix_info['NEXT_SAC_DURATION']))
                                trial_word_data.at[widx, 'saccade_vels'].append(float(fix_info['NEXT_SAC_PEAK_VELOCITY'].replace(',', '.')))
                else:
                    UNMAPPED += 1
                    if fix_info['CURRENT_FIX_NEAREST_INTEREST_AREA'] in char_id_list:
                        dists.append(float(fix_info['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE'].replace(',', '.')))
                        if float(fix_info['CURRENT_FIX_NEAREST_INTEREST_AREA_DISTANCE'].replace(',', '.')) < 1:
                            DIST += 1

            # now process word features that need previously added fixation features
            fixations_to_left_of_curr_fix = []
            for word_ind, word in trial_word_data.iterrows():

                if len(word["fixation_durs"]) != 0:
                    trial_word_data.loc[word_ind, 'word_mean_fix_dur'] = np.mean(word['fixation_durs'])
                    go_past_fix = []
                    first_pass_fix = []
                    # check for saccades
                    if len(word["saccade_durs"]) != 0:
                        trial_word_data.loc[word_ind, 'word_mean_sacc_dur'] = np.mean(word['saccade_durs'])
                        trial_word_data.loc[word_ind, 'word_peak_sacc_velocity'] = np.max(word['saccade_vels'])

                    for idx, f in enumerate(word['trial_fix_ids']):
                        if idx == 0:
                            go_past_fix.append(f)
                            first_pass_fix.append(f)
                            if idx != len(word['trial_fix_ids'])-1:
                                i = 1
                                # keep track of previous fixations in the trial
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
                        if np.isnan(trial_word_data.loc[word_ind, 'word_first_pass_dur']):
                            trial_word_data.loc[word_ind, 'word_first_pass_dur'] = trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']
                        else:
                            trial_word_data.loc[word_ind, 'word_first_pass_dur'] += trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']
                    for fix_ind in go_past_fix:
                        if np.isnan(trial_word_data.loc[word_ind, 'word_go_past_time']):
                            trial_word_data.loc[word_ind, 'word_go_past_time'] = trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']
                        else:
                            trial_word_data.loc[word_ind, 'word_go_past_time'] += trial_data.loc[fix_ind, 'CURRENT_FIX_DURATION']
            # concatenate all trials
            #print(trial_word_data['trialId'].unique(), trial_word_data['speechId'].unique())
            words_df = pd.concat([words_df, trial_word_data], ignore_index=True)
        # reorder columns
        words_df = words_df[['part','trialId','speechId','paragraphId','sentenceId','wordId','word','char_IA_ids','landing_position','word_first_fix_dur', 'word_first_pass_dur','word_go_past_time','word_mean_fix_dur','word_total_fix_dur','number_of_fixations','word_mean_sacc_dur','word_peak_sacc_velocity']]
        WORDS += len(words_df)
        # todo: try sorting by trialID and speechID
        words_df = words_df.sort_values(['speechId', 'trialId'])
        #trials_after = words_df.groupby(["trialId"])
        #print(len(trials_after))
        words_df.to_csv(output_dir+subject+".csv", index=False, encoding='utf-8')

print()
print(TOTAL_FIX, " total unfiltered fixations from exported reports.")
print(WORDS, " total words with IAs.")
print(ALL_FIX_IN_IA, " total fixations within IAs.")
print(UNMAPPED, " unmapped fixations, ", (UNMAPPED/ALL_FIX_IN_IA))
print(DIST, " with tiny distance", (DIST/UNMAPPED), "% could be fixed easily.")
print(len(dists), np.mean(dists), np.median(dists), np.min(dists), np.max(dists))
